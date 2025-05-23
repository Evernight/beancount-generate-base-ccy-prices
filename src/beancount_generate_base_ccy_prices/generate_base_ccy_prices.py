"""A plugin that inserts an additional price to the base rate by applying
fx rate to a price.

Original can be found at:
https://github.com/tarioch/beancounttools/blob/master/src/tariochbctools/plugins/generate_base_ccy_prices.py
"""
from beancount.core import amount, data, prices
from collections import defaultdict

__plugins__ = ["generate"]

def generate(entries, options_map, baseCcy):
    errors = []
    priceMap = prices.build_price_map(entries)
    existingDates = defaultdict(None)

    # print(f'\n\npass for {baseCcy}')
    additionalEntries = []
    for entry in entries:
        if isinstance(entry, data.Price) and entry.amount.currency != baseCcy:
            fxTuple = tuple([entry.amount.currency, baseCcy])
            fxRate = prices.get_price(priceMap, fxTuple, entry.date)

            if not fxRate[1]:
                continue

            pair = (entry.currency, baseCcy)
            if pair not in existingDates:
                existingDates[pair] = set([item[0] for item in priceMap.get(pair, [])])
            if entry.date in existingDates[pair]:
                continue

            # print(f'{str(entry.date)} price for {entry.currency} in {baseCcy}  through {entry.amount.currency}')
            priceInBaseCcy = amount.Amount(entry.amount.number * fxRate[1], baseCcy)

            additionalEntries.append(
                data.Price(entry.meta, entry.date, entry.currency, priceInBaseCcy)
            )

            existingDates[pair].add(entry.date)

    entries.extend(additionalEntries)

    return entries, errors
