#!/usr/bin/env bash

# use yq as jq even if jq is not installed
if command -v 'yq' &>/dev/null
then
  jq() {
    yq ${@}
  }
fi

set -euo pipefail

# script base data
_DEPS=(curl jq)
_VER="0.1.0"
_APP=$(basename "$0")

# option names (long and short)
_LONG_OPTS="help,version,list,all"
_OPTS="hvla"

# global variables to store shell options
OPT_LIST=0
OPT_ALL=0

# base url for the API, override with BASE_URL env var if needed
BASE_URL="${BASE_URL:-http://localhost:5000}"

# shows help documentation message
_usage() {
  cat <<EOF
${_APP} - Version ${_VER}

  Smoke-test script for the pyissues-api. Each test_* function hits one
  endpoint and prints the response. Run a single test by name, list all
  available tests, or run everything at once.

  USAGE:
    ${_APP} [...OPTIONS] -- [FUNCTION_NAME]

  OPTIONS:
    -h --help              Shows this help message.
    -v --version           Shows the script version.
    -l --list              Lists all available test functions.
    -a --all               Runs all test functions.

  EXAMPLES:
    ${_APP} -- test_health
    ${_APP} --list
    ${_APP} --all

  DEPENDENCIES:
    (${#_DEPS[@]}) ${_DEPS[@]}
EOF
}

# logs an error message and exit with a custom code
throw() {
  >&2 echo "${_APP}: $2"
  exit "$1"
}

# apply the options into usable variables while filtering for the arguments
_ARGV=$(getopt -o "${_OPTS}" -l "${_LONG_OPTS}" -n "${_APP}" -- "$@")

eval "set -- ${_ARGV}"

while true
do
  case $1 in
    -h | --help)     _usage;          exit ;;
    -v | --version)  echo "${_VER}";  exit ;;
    -l | --list)     OPT_LIST=1; shift ;;
    -a | --all)      OPT_ALL=1;  shift ;;
    --) shift; break ;;
     *) throw 1 "invalid option -- '$1'" ;;
  esac
done

# dependency check before running the script body
for dep in "${_DEPS[@]}"
do
  command -v "${dep}" &>/dev/null ||
    throw 1 "dependency not satisfied -- '${dep}'"
done

unset _ARGV _LONG_OPTS _OPTS

# unique id
uid() {
  echo "$(date +%s)$RANDOM"
}

# registers a throwaway user, logs in, and prints just the JWT token
_get_token() {
  local kevin_uid=kevin_$(uid)

  curl -s -X POST "${BASE_URL}/auth/register" \
    -H "Content-Type: application/json" \
    -d '{"username": "'"$kevin_uid"'", "email": "'"$kevin_uid"'@example.com", "password": "secret123"}' \
    >/dev/null

  curl -s -X POST "${BASE_URL}/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"username": "'"$kevin_uid"'", "password": "secret123"}' |
    jq -r '.token'
}

# creates a project with the given token, prints just its id
_create_project() {
  local token="$1"
  local name="${2:-Smoke Project}"

  curl -s -X POST "${BASE_URL}/projects" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${token}" \
    -d '{"name": "'"$name"'", "description": "created for smoke testing"}' |
    jq -r '.id'
}

# creates an issue in the given project with the given token, prints just its id
_create_issue() {
  local token="$1"
  local project_id="$2"
  local title="${3:-Smoke Issue}"

  curl -s -X POST "${BASE_URL}/projects/${project_id}/issues" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${token}" \
    -d '{"title": "'"$title"'", "description": "created for smoke testing"}' |
    jq -r '.id'
}

# TEST FUNCTIONS
# --------------
# each one should:
# - call the endpoint with curl
# - pretty-print the response with jq
# - print a short label so output is easy to scan

test_create_comment() {
  local token project_id issue_id
  token=$(_get_token)
  project_id=$(_create_project "$token")
  issue_id=$(_create_issue "$token" "$project_id")

  jq <<<'{"/projects/<id>/issues/<id>/comments": "POST"}'
  curl -s -X POST "${BASE_URL}/projects/${project_id}/issues/${issue_id}/comments" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${token}" \
    -d '{"body": "This needs more detail in the description"}' | jq
}

test_create_comment_missing_body() {
  local token project_id issue_id
  token=$(_get_token)
  project_id=$(_create_project "$token")
  issue_id=$(_create_issue "$token" "$project_id")

  jq <<<'{"/projects/<id>/issues/<id>/comments (missing body)": "POST"}'
  curl -s -X POST "${BASE_URL}/projects/${project_id}/issues/${issue_id}/comments" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${token}" \
    -d '{}' | jq
}

test_list_comments() {
  local token project_id issue_id
  token=$(_get_token)
  project_id=$(_create_project "$token")
  issue_id=$(_create_issue "$token" "$project_id")

  curl -s -X POST "${BASE_URL}/projects/${project_id}/issues/${issue_id}/comments" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${token}" \
    -d '{"body": "First comment"}' >/dev/null

  curl -s -X POST "${BASE_URL}/projects/${project_id}/issues/${issue_id}/comments" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${token}" \
    -d '{"body": "Second comment"}' >/dev/null

  jq <<<'{"/projects/<id>/issues/<id>/comments": "GET"}'
  curl -s "${BASE_URL}/projects/${project_id}/issues/${issue_id}/comments" \
    -H "Authorization: Bearer ${token}" | jq
}

test_comment_full_lifecycle() {
  local token project_id issue_id id
  token=$(_get_token)
  project_id=$(_create_project "$token")
  issue_id=$(_create_issue "$token" "$project_id")

  jq <<<'{"/projects/<id>/issues/<id>/comments (create)": "POST"}'
  id=$(curl -s -X POST "${BASE_URL}/projects/${project_id}/issues/${issue_id}/comments" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${token}" \
    -d '{"body": "before update"}' | tee /dev/stderr | jq -r '.id')

  jq <<<'{"/projects/<id>/issues/<id>/comments/<id> (get)": "GET"}'
  curl -s "${BASE_URL}/projects/${project_id}/issues/${issue_id}/comments/${id}" \
    -H "Authorization: Bearer ${token}" | jq

  jq <<<'{"/projects/<id>/issues/<id>/comments/<id> (update)": "PUT"}'
  curl -s -X PUT "${BASE_URL}/projects/${project_id}/issues/${issue_id}/comments/${id}" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${token}" \
    -d '{"body": "after update"}' | jq

  jq <<<'{"/projects/<id>/issues/<id>/comments/<id> (delete)": "DELETE"}'
  curl -s -o /dev/null -w "status: %{http_code}\n" -X DELETE \
    "${BASE_URL}/projects/${project_id}/issues/${issue_id}/comments/${id}" \
    -H "Authorization: Bearer ${token}"

  jq <<<'{"/projects/<id>/issues/<id>/comments/<id> (get after delete)": "GET"}'
  curl -s "${BASE_URL}/projects/${project_id}/issues/${issue_id}/comments/${id}" \
    -H "Authorization: Bearer ${token}" | jq
}

test_comment_wrong_author() {
  local token_a token_b project_id issue_id id
  token_a=$(_get_token)
  token_b=$(_get_token)
  project_id=$(_create_project "$token_a")
  issue_id=$(_create_issue "$token_a" "$project_id")

  id=$(curl -s -X POST "${BASE_URL}/projects/${project_id}/issues/${issue_id}/comments" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${token_a}" \
    -d '{"body": "written by A"}' | jq -r '.id')

  jq <<<'{"/projects/<id>/issues/<id>/comments/<id> (update with B'"'"'s token, should fail)": "PUT"}'
  curl -s -X PUT "${BASE_URL}/projects/${project_id}/issues/${issue_id}/comments/${id}" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${token_b}" \
    -d '{"body": "hijacked"}' | jq

  jq <<<'{"/projects/<id>/issues/<id>/comments/<id> (delete with B'"'"'s token, should fail)": "DELETE"}'
  curl -s -X DELETE "${BASE_URL}/projects/${project_id}/issues/${issue_id}/comments/${id}" \
    -H "Authorization: Bearer ${token_b}" | jq
}

test_comment_unauthorized() {
  local token project_id issue_id
  token=$(_get_token)
  project_id=$(_create_project "$token")
  issue_id=$(_create_issue "$token" "$project_id")

  jq <<<'{"/projects/<id>/issues/<id>/comments (no token, should fail)": "POST"}'
  curl -s -X POST "${BASE_URL}/projects/${project_id}/issues/${issue_id}/comments" \
    -H "Content-Type: application/json" \
    -d '{"body": "no auth header"}' | jq
}

test_create_issue() {
  local token project_id
  token=$(_get_token)
  project_id=$(_create_project "$token")

  jq <<<'{"/projects/<id>/issues": "POST"}'
  curl -s -X POST "${BASE_URL}/projects/${project_id}/issues" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${token}" \
    -d '{"title": "Fix login bug", "description": "Users can'\''t log in with email"}' | jq
}

test_create_issue_invalid_priority() {
  local token project_id
  token=$(_get_token)
  project_id=$(_create_project "$token")

  jq <<<'{"/projects/<id>/issues (invalid priority)": "POST"}'
  curl -s -X POST "${BASE_URL}/projects/${project_id}/issues" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${token}" \
    -d '{"title": "Bad priority", "priority": "urgent"}' | jq
}

test_list_issues_with_status_filter() {
  local token project_id id_a id_b
  token=$(_get_token)
  project_id=$(_create_project "$token")

  id_a=$(curl -s -X POST "${BASE_URL}/projects/${project_id}/issues" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${token}" \
    -d '{"title": "Issue A"}' | jq -r '.id')

  id_b=$(curl -s -X POST "${BASE_URL}/projects/${project_id}/issues" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${token}" \
    -d '{"title": "Issue B"}' | jq -r '.id')

  # move issue B to "doing"
  curl -s -X PUT "${BASE_URL}/projects/${project_id}/issues/${id_b}" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${token}" \
    -d '{"title": "Issue B", "status": "doing"}' >/dev/null

  jq <<<'{"/projects/<id>/issues?status=todo": "GET"}'
  curl -s "${BASE_URL}/projects/${project_id}/issues?status=todo" \
    -H "Authorization: Bearer ${token}" | jq

  jq <<<'{"/projects/<id>/issues?status=doing": "GET"}'
  curl -s "${BASE_URL}/projects/${project_id}/issues?status=doing" \
    -H "Authorization: Bearer ${token}" | jq
}

test_issue_full_lifecycle() {
  local token project_id id
  token=$(_get_token)
  project_id=$(_create_project "$token")

  jq <<<'{"/projects/<id>/issues (create)": "POST"}'
  id=$(curl -s -X POST "${BASE_URL}/projects/${project_id}/issues" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${token}" \
    -d '{"title": "Lifecycle issue", "description": "before update"}' | tee /dev/stderr | jq -r '.id')

  jq <<<'{"/projects/<id>/issues/<id> (get)": "GET"}'
  curl -s "${BASE_URL}/projects/${project_id}/issues/${id}" \
    -H "Authorization: Bearer ${token}" | jq

  jq <<<'{"/projects/<id>/issues/<id> (todo -> doing)": "PUT"}'
  curl -s -X PUT "${BASE_URL}/projects/${project_id}/issues/${id}" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${token}" \
    -d '{"title": "Lifecycle issue", "description": "in progress", "status": "doing"}' | jq

  jq <<<'{"/projects/<id>/issues/<id> (doing -> done)": "PUT"}'
  curl -s -X PUT "${BASE_URL}/projects/${project_id}/issues/${id}" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${token}" \
    -d '{"title": "Lifecycle issue", "description": "finished", "status": "done", "priority": "high"}' | jq

  jq <<<'{"/projects/<id>/issues/<id> (delete)": "DELETE"}'
  curl -s -o /dev/null -w "status: %{http_code}\n" -X DELETE "${BASE_URL}/projects/${project_id}/issues/${id}" \
    -H "Authorization: Bearer ${token}"

  jq <<<'{"/projects/<id>/issues/<id> (get after delete)": "GET"}'
  curl -s "${BASE_URL}/projects/${project_id}/issues/${id}" \
    -H "Authorization: Bearer ${token}" | jq
}

test_issue_invalid_status_transition() {
  local token project_id id
  token=$(_get_token)
  project_id=$(_create_project "$token")

  id=$(curl -s -X POST "${BASE_URL}/projects/${project_id}/issues" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${token}" \
    -d '{"title": "Cannot skip to done"}' | jq -r '.id')

  jq <<<'{"/projects/<id>/issues/<id> (todo -> done, should fail)": "PUT"}'
  curl -s -X PUT "${BASE_URL}/projects/${project_id}/issues/${id}" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${token}" \
    -d '{"title": "Cannot skip to done", "status": "done"}' | jq
}

test_issue_wrong_owner() {
  local token_a token_b project_id id
  token_a=$(_get_token)
  token_b=$(_get_token)
  project_id=$(_create_project "$token_a")

  id=$(curl -s -X POST "${BASE_URL}/projects/${project_id}/issues" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${token_a}" \
    -d '{"title": "Owned by A"}' | jq -r '.id')

  jq <<<'{"/projects/<id>/issues/<id> (get with B'"'"'s token)": "GET"}'
  curl -s "${BASE_URL}/projects/${project_id}/issues/${id}" \
    -H "Authorization: Bearer ${token_b}" | jq
}

test_create_project_unauthorized() {
  jq <<<'{"/projects (no token)": "POST"}'
  curl -s -X POST "${BASE_URL}/projects" \
    -H "Content-Type: application/json" \
    -d '{"name": "Should fail", "description": "no auth header"}' | jq
}

test_create_project() {
  local token
  token=$(_get_token)

  jq <<<'{"/projects": "POST"}'
  curl -s -X POST "${BASE_URL}/projects" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${token}" \
    -d '{"name": "Pocket Tracker", "description": "MVP project"}' | jq
}

test_list_projects() {
  local token
  token=$(_get_token)

  curl -s -X POST "${BASE_URL}/projects" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${token}" \
    -d '{"name": "Project A", "description": "first"}' >/dev/null

  curl -s -X POST "${BASE_URL}/projects" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${token}" \
    -d '{"name": "Project B", "description": "second"}' >/dev/null

  jq <<<'{"/projects": "GET"}'
  curl -s "${BASE_URL}/projects" \
    -H "Authorization: Bearer ${token}" | jq
}

test_project_full_lifecycle() {
  local token id

  token=$(_get_token)

  jq <<<'{"/projects (create)": "POST"}'
  id=$(curl -s -X POST "${BASE_URL}/projects" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${token}" \
    -d '{"name": "Lifecycle Project", "description": "before update"}' | tee /dev/stderr | jq -r '.id')

  jq <<<'{"/projects/<id> (get)": "GET"}'
  curl -s "${BASE_URL}/projects/${id}" \
    -H "Authorization: Bearer ${token}" | jq

  jq <<<'{"/projects/<id> (update)": "PUT"}'
  curl -s -X PUT "${BASE_URL}/projects/${id}" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${token}" \
    -d '{"name": "Lifecycle Project (renamed)", "description": "after update"}' | jq

  jq <<<'{"/projects/<id> (delete)": "DELETE"}'
  curl -s -o /dev/null -w "status: %{http_code}\n" -X DELETE "${BASE_URL}/projects/${id}" \
    -H "Authorization: Bearer ${token}"

  jq <<<'{"/projects/<id> (get after delete)": "GET"}'
  curl -s "${BASE_URL}/projects/${id}" \
    -H "Authorization: Bearer ${token}" | jq
}

test_project_wrong_owner() {
  local token_a token_b id

  token_a=$(_get_token)
  token_b=$(_get_token)

  id=$(curl -s -X POST "${BASE_URL}/projects" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${token_a}" \
    -d '{"name": "Owned by A", "description": null}' | jq -r '.id')

  jq <<<'{"/projects/<id> (get with B'"'"'s token)": "GET"}'
  curl -s "${BASE_URL}/projects/${id}" \
    -H "Authorization: Bearer ${token_b}" | jq
}

test_health() {
  jq <<<'{"/health": "GET"}'
  curl -s "${BASE_URL}/health" | jq
}

test_register() {
  jq <<<'{"/auth/register": "POST"}'
  curl -s -X POST "${BASE_URL}/auth/register" \
    -H "Content-Type: application/json" \
    -d '{
      "username": "kevin_'"$(uid)"'",
      "email": "kevin_'"$(uid)"'@example.com",
      "password": "secret123"
    }' | jq
}

test_login_missing_fields() {
  jq <<<'{"/auth/login (missing password)": "POST"}'
  curl -s -X POST "${BASE_URL}/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"username": "kevin_'"$(uid)"'"}' | jq
}

test_register_and_login() {
  local kevin_uid=kevin_$(uid)

  jq <<<'{"/auth/register + /auth/login": "POST"}'

  curl -s -X POST "${BASE_URL}/auth/register" \
    -H "Content-Type: application/json" \
    -d '{"username": "'"$kevin_uid"'", "email": "'"$kevin_uid"'@example.com", "password": "secret123"}' | jq

  curl -s -X POST "${BASE_URL}/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"username": "'"$kevin_uid"'", "password": "secret123"}' | jq
}

# Add new tests below following the same pattern, e.g.:
#
# test_register() {
#   jq <<<'{"/auth/register": "POST"}'
#   curl -s -X POST "${BASE_URL}/auth/register" \
#     -H "Content-Type: application/json" \
#     -d '{"username": "kevin", "password": "secret123"}' | jq
# }
#
# test_login() {
#   jq <<<'{"/auth/login": "POST"}'
#   curl -s -X POST "${BASE_URL}/auth/login" \
#     -H "Content-Type: application/json" \
#     -d '{"username": "kevin", "password": "secret123"}' | jq
# }

_list_tests() {
  declare -F |
    awk '{print $3}' |
    grep '^test_'
}

_run_all() {
  for fn in $(_list_tests)
  do
    "${fn}"
    echo
  done
}

if [[ "${OPT_LIST}" -eq 1 ]]
then
  _list_tests
  exit 0
fi

if [[ "${OPT_ALL}" -eq 1 ]]
then
  _run_all
  exit 0
fi

[[ $# -ge 1 ]] ||
  throw 1 "missing function name (use --list to see options)"

fn="$1"

if ! declare -F "${fn}" &>/dev/null
then
  throw 1 "unknown test -- '${fn}' (use --list to see options)"
fi

"${fn}"
