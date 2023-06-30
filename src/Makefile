lint:
	python3 -m pylint --fail-under=9.5 $$(find . -name "*.py" -not -path "./tests/*")
	find . -name "*.py" -not -path "./tests/*" -exec darglint {} \;
	find . -name "*.py" -not -path "./tests/*" -exec pydocstyle {} \;

format:
	find . -name "*.py" -not -path "./tests/*" -exec python3 -m isort {} \; -exec python3 -m black {} \;