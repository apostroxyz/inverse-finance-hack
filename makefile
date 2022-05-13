.ONESHELL:

install-all:
	npm install -g ganache@7.0.3
	pip install -r requirements.txt
	yarn
	brownie networks import ./network-config.yml True

clean:
	rm -rf build OpenZeppelin node_modules yearn