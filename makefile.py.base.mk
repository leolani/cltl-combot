.PHONY: py-clean
py-clean:
	$(info Clean $(project_name))
	@rm -rf venv
	@rm -rf dist

venv:
	python -m venv venv
	source venv/bin/activate; \
		pip install -r requirements.txt --no-index \
			--find-links="$(project_mirror)" --find-links="$(project_repo)"; \
		deactivate

build: dist

test:
	source venv/bin/activate; \
		python -m unittest; \
		deactivate

dist: venv
	$(info Create distribution for $(project_name))
	source venv/bin/activate; \
		python setup.py sdist; \
		deactivate

py-install: dist
	$(info Install $(project_name))
	@rm -rf $(project_repo)/$(project_name).{0..9}*.tar.gz
	@cp dist/*.tar.gz $(project_repo)
