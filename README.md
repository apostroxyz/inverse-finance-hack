# Reproducing the Inverse Finance hack

What hacker did:
- Swap 500 ETH to INV in #14506358 https://etherscan.io/tx/0x20a6dcff06a791a7f8be9f423053ce8caee3f9eecc31df32445fc98d4ccd8365
- Hack Inverse in #14506359 https://etherscan.io/tx/0x600373f67521324c8068cfd025f121a0843d57ec813411661b07edc5ff781842

## Development

### Clone repository

- clone using HTTPS
  ```bash
  git clone https://github.com/apostroxyz/inverse-finance-hack.git
  ```
- or SSH
  ```bash
  git clone git@github.com:apostroxyz/inverse-finance-hack.git
  ```
- change directory to inverse-finance-hack
  ```bash
  cd inverse-finance-hack
  ```

### Setup environment

#### VSCode + Docker (recommended)

- install [Docker](https://docs.docker.com/get-docker/)
- install [VSCode](https://code.visualstudio.com/)
- install [Remote - Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) VSCode extension
- open cloned repository in VSCode
- click F1 and run `>Remote-Containers: Reopen in Container`
- wait until all dependencies are installed (you will see the message "Done. Press any key to close the terminal." in the terminal `Configuring`)

#### Local

- you will need Python 3.8 and Node.js >=14.x
- install dependencies:
  ```bash
  make clean && make install-all
  ```

### Setup .env

- run `cp .example.env .env`
- insert keys into `.env`

### Hack Inverse Finance on mainnet fork

Run brownie console with predefined contracts and scripts

```bash
yarn hack
```

In console you can:

- use predefined `thief` account
- interact with
  - assets using `weth`, `inv`, `dola`, `usdc`, `wbtc`, `yfi`, for example `weth.balanceOf(thief)`
  - sushiswap contracts using `sushi_router`, `inv_weth_pair`, for example `inv_weth_pair.getReserves()`
  - oracle contracts using `oracle`, `keep_3r_v2_oracle_factory`, `keep_3r_v2_feed`, `eth_feed`
  - curve pool using `curve_pool`
  - Inverse Finance comptroller using `comptroller`
  - Inverse Finance anchors (cTokens) using `xinv`, `anwbtc`, `anyfi`, `aneth`, `andola`
- print current oracle prices using `print_prices()`
- hack Inverse Finance using `hack_inverse()`
- check `thief` ETH balance using `web3.eth.getBalance(thief.address)`
- print transaction events using `chain.get_transaction("0xcfd26...").info()`
