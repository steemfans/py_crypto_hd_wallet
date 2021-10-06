# Copyright (c) 2021 Emanuele Bellocchia
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


# Imports
from bip_utils import (
    MoneroChecksumError, MoneroMnemonicGenerator, MoneroSeedGenerator,
    MoneroKeyError, Monero
)
from py_crypto_hd_wallet.monero.hd_wallet_monero_enum import (
    HdWalletMoneroWordsNum, HdWalletMoneroLanguages
)
from py_crypto_hd_wallet.monero.hd_wallet_monero import HdWalletMonero
from py_crypto_hd_wallet.common import HdWalletBase
from py_crypto_hd_wallet.utils import Utils


class HdWalletMoneroFactory:
    """ HD wallet Monero factory class. It allows a HdWalletMonero to be created in different way. """

    def __init__(self) -> None:
        """ Construct class.
        The class does not have any member, but the constructor is kept to maintain the same syntax
        of the other factories (e.g. Factory().CreateRandom(...)).
        """
        pass

    @staticmethod
    def CreateRandom(wallet_name: str,
                     words_num: HdWalletMoneroWordsNum = HdWalletMoneroWordsNum.WORDS_NUM_25,
                     lang: HdWalletMoneroLanguages = HdWalletMoneroLanguages.ENGLISH) -> HdWalletBase:
        """ Create wallet randomly.

        Args:
            wallet_name (str)                           : Wallet name
            words_num (HdWalletMoneroWordsNum, optional): Words number (default: 25)
            lang (HdWalletMoneroLanguages, optional)    : Language (default: English)

        Returns:
            HdWalletBase object: HdWalletBase object

        Raises:
            TypeError: If words number is not a HdWalletMoneroWordsNum enum or language is not a HdWalletMoneroLanguages enum
        """
        if not isinstance(words_num, HdWalletMoneroWordsNum):
            raise TypeError("Words number is not an enumerative of HdWalletMoneroWordsNum")
        elif not isinstance(lang, HdWalletMoneroLanguages):
            raise TypeError("Language is not an enumerative of HdWalletMoneroLanguages")

        mnemonic = MoneroMnemonicGenerator(lang).FromWordsNumber(words_num)

        return HdWalletMoneroFactory.CreateFromMnemonic(wallet_name, mnemonic.ToStr())

    @staticmethod
    def CreateFromMnemonic(wallet_name: str,
                           mnemonic: str) -> HdWalletBase:
        """ Create wallet from mnemonic.

        Args:
            wallet_name (str): Wallet name
            mnemonic (str)   : Mnemonic

        Returns:
            HdWalletBase object: HdWalletBase object

        Raises:
            ValueError: If the mnemonic is not valid
        """
        try:
            seed_bytes = MoneroSeedGenerator(mnemonic).Generate()
        except (ValueError, MoneroChecksumError) as ex:
            raise ValueError(f"Invalid mnemonic: {mnemonic}") from ex

        monero_obj = Monero.FromSeed(seed_bytes)

        return HdWalletMonero(wallet_name=wallet_name,
                              monero_obj=monero_obj,
                              mnemonic=mnemonic,
                              seed_bytes=seed_bytes)

    @staticmethod
    def CreateFromSeed(wallet_name: str,
                       seed_bytes: bytes) -> HdWalletBase:
        """ Create wallet from seed.

        Args:
            wallet_name (str) : Wallet name
            seed_bytes (bytes): Seed bytes

        Returns:
            HdWalletBase object: HdWalletBase object

        Raises:
            ValueError: If the seed is not valid
        """
        monero_obj = Monero.FromSeed(seed_bytes)

        return HdWalletMonero(wallet_name=wallet_name,
                              monero_obj=monero_obj,
                              seed_bytes=seed_bytes)

    @staticmethod
    def CreateFromPrivateKey(wallet_name: str,
                             priv_skey: bytes) -> HdWalletBase:
        """ Create wallet from private spend key.

        Args:
            wallet_name (str): Wallet name
            priv_skey (bytes): Private spend key bytes

        Returns:
            HdWalletBase object: HdWalletBase object

        Raises:
            ValueError: If the private key is not valid
        """
        try:
            monero_obj = Monero.FromPrivateSpendKey(priv_skey)
        except MoneroKeyError as ex:
            raise ValueError(f"Invalid private spend key: {Utils.BytesToHexString(priv_skey)}") from ex

        return HdWalletMonero(wallet_name=wallet_name,
                              monero_obj=monero_obj)

    @staticmethod
    def CreateFromWatchOnly(wallet_name: str,
                            priv_vkey: bytes,
                            pub_skey: bytes) -> HdWalletBase:
        """ Create wallet from private view key and public spend key (i.e. watch-only wallet).

        Args:
            wallet_name (str): Wallet name
            priv_vkey (bytes): Private view key bytes
            pub_skey (bytes) : Public spend key bytes

        Returns:
            HdWalletBase object: HdWalletBase object

        Raises:
            ValueError: If the public key is not valid
        """
        try:
            monero_obj = Monero.FromWatchOnly(priv_vkey, pub_skey)
        except MoneroKeyError as ex:
            raise ValueError(f"Invalid keys for watch-only wallet") from ex

        return HdWalletMonero(wallet_name=wallet_name,
                              monero_obj=monero_obj)