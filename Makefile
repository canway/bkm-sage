.PHONY: build

VER := $(shell poetry version -s)

init:
	poetry install

test:
	pytest tests -s

build-sdk:
	@echo "Start to build sdk ..."
	poetry check
	poetry build -f sdist
	@echo "Build success."

build-toolkit:
	@echo "Start to build toolkit ..."
	sed -i "s/name = \"bkm_sage\"/name = \"bkm_sage_toolkit\"/g" pyproject.toml
	poetry build -f sdist
	sed -i "s/name = \"bkm_sage_toolkit\"/name = \"bkm_sage\"/g" pyproject.toml
	@echo "Build success."


build-bundle:
	@echo "Start to build bundle ..."
	rm -rf dist
	mkdir -p dist/bkm_sage_bundle-$(VER)
	poetry check
	poetry run pyinstaller --onefile --distpath dist/bkm_sage_bundle-${VER} --name bkm-sage main.py
	cp -rf extend_tools ./dist/bkm_sage_bundle-${VER}/
	cd ./dist && tar -czvf bkm_sage_bundle-${VER}.tar.gz ./bkm_sage_bundle-${VER}; rm -rf ./bkm_sage_bundle-${VER}
	@echo "Build success"


pyinstaller-onefile:
	echo "Start to build bundle with pyinstaller ..."
	poetry check
	poetry run pyinstaller --onefile --name bkm-sage main.py
	echo "bkm-sage bundle in dist directory"


dumps-wiki:
	@echo "Start to dumps WiKi ..."
	poetry check
	poetry run python dumps.py dumps --docPath=docs
	@echo "Dumps WiKi success."
