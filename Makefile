.PHONY: default install

default:
	find . -type f \( -name '*.pyc' -or -name '.DS_Store' \) -exec rm -rf {} \; && cd 'Dict - Lookup Word' && zip -r ../dict.alfredworkflow .

install:
	open -a 'Alfred 2.app' dict.alfredworkflow
