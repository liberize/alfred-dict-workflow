.PHONY: default install

default:
	find . -type f \( -name '*.pyc' -or -name '.DS_Store' \) -exec rm -rf '{}' \; && \
	zip -r dict.alfredworkflow . -x Makefile -x '*.md' -x '*.gif' -x '.git*'

install:
	open dict.alfredworkflow
