.PHONY: clean
clean:
	@find . \( -type d \( -name ".venv" -o -name "venv" \) -prune \) \
		-o -type d -name "__pycache__" -exec rm -vrf {} +
