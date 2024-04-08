import logging
import requests

from functools import cache
from typing import Optional

from django.conf import settings

from eth_typing import ChecksumAddress

from gnosis.eth import EthereumClient, EthereumClientProvider, EthereumNetwork
from gnosis.eth.clients import (
    BlockscoutClient as BaseBlockscoutClient,
    BlockScoutConfigurationProblem,
    ContractMetadata,
    EtherscanClient,
    EtherscanClientConfigurationProblem,
    SourcifyClient,
    SourcifyClientConfigurationProblem,
)

from ..abis import butter_router_v2_metadata, butter_router_v2

logger = logging.getLogger(__name__)


DEFAULT_ABI_MAP = {
    butter_router_v2: butter_router_v2_metadata,
}


@cache
def get_contract_metadata_service():
    return ContractMetadataService(EthereumClientProvider(), settings.ETHERSCAN_API_KEY)


class BlockscoutClient(BaseBlockscoutClient):
    NETWORK_WITH_URL = {
        EthereumNetwork.GNOSIS: "https://gnosis.blockscout.com/api/v1/graphql",
        EthereumNetwork.ENERGY_WEB_CHAIN: "https://explorer.energyweb.org/graphiql",
        EthereumNetwork.ENERGY_WEB_VOLTA_TESTNET: "https://volta-explorer.energyweb.org/graphiql",
        EthereumNetwork.POLIS_MAINNET: "https://explorer.polis.tech/graphiql",
        EthereumNetwork.BOBA_NETWORK: "https://blockexplorer.boba.network/graphiql",
        EthereumNetwork.GATHER_DEVNET_NETWORK: "https://devnet-explorer.gather.network/graphiql",
        EthereumNetwork.GATHER_TESTNET_NETWORK: "https://testnet-explorer.gather.network/graphiql",
        EthereumNetwork.GATHER_MAINNET_NETWORK: "https://explorer.gather.network/graphiql",
        EthereumNetwork.METIS_GOERLI_TESTNET: "https://goerli.explorer.metisdevops.link/graphiql",
        EthereumNetwork.METIS_ANDROMEDA_MAINNET: "https://andromeda-explorer.metis.io/graphiql",
        EthereumNetwork.FUSE_MAINNET: "https://explorer.fuse.io/graphiql",
        EthereumNetwork.VELAS_EVM_MAINNET: "https://evmexplorer.velas.com/graphiql",
        EthereumNetwork.REI_NETWORK: "https://scan.rei.network/graphiql",
        EthereumNetwork.REI_CHAIN_TESTNET: "https://scan-test.rei.network/graphiql",
        EthereumNetwork.METER_MAINNET: "https://scan.meter.io/graphiql",
        EthereumNetwork.METER_TESTNET: "https://scan-warringstakes.meter.io/graphiql",
        EthereumNetwork.GODWOKEN_TESTNET_V1: "https://v1.betanet.gwscan.com/graphiql",
        EthereumNetwork.GODWOKEN_MAINNET: "https://v1.gwscan.com/graphiql",
        EthereumNetwork.VENIDIUM_TESTNET: "https://evm-testnet.venidiumexplorer.com/graphiql",
        EthereumNetwork.VENIDIUM_MAINNET: "https://evm.venidiumexplorer.com/graphiql",
        EthereumNetwork.KLAYTN_TESTNET_BAOBAB: "https://baobab.scope.klaytn.com/graphiql",
        EthereumNetwork.KLAYTN_MAINNET_CYPRESS: "https://scope.klaytn.com/graphiql",
        EthereumNetwork.ACALA_NETWORK: "https://blockscout.acala.network/graphiql",
        EthereumNetwork.KARURA_NETWORK_TESTNET: "https://blockscout.karura.network/graphiql",
        EthereumNetwork.ASTAR: "https://blockscout.com/astar/graphiql",
        EthereumNetwork.SHIDEN: "https://blockscout.com/shiden/graphiql",
        EthereumNetwork.EVMOS: "https://evm.evmos.org/graphiql",
        EthereumNetwork.EVMOS_TESTNET: "https://evm.evmos.dev/graphiql",
        EthereumNetwork.KCC_MAINNET: "https://scan.kcc.io/graphiql",
        EthereumNetwork.KCC_TESTNET: "https://scan-testnet.kcc.network/graphiql",
        EthereumNetwork.CROSSBELL: "https://scan.crossbell.io/graphiql",
        EthereumNetwork.ETHEREUM_CLASSIC: "https://blockscout.com/etc/mainnet/graphiql",
        EthereumNetwork.MORDOR_TESTNET: "https://blockscout.com/etc/mordor/graphiql",
        EthereumNetwork.SCROLL_SEPOLIA_TESTNET: "https://sepolia-blockscout.scroll.io/graphiql",
        EthereumNetwork.MANTLE: "https://explorer.mantle.xyz/graphiql",
        EthereumNetwork.MANTLE_TESTNET: "https://explorer.testnet.mantle.xyz/graphiql",
        EthereumNetwork.JAPAN_OPEN_CHAIN_MAINNET: "https://mainnet.japanopenchain.org/graphiql",
        EthereumNetwork.JAPAN_OPEN_CHAIN_TESTNET: "https://explorer.testnet.japanopenchain.org/graphiql",
        EthereumNetwork.ZETACHAIN_ATHENS_3_TESTNET: "https://zetachain-athens-3.blockscout.com/graphiql",
        EthereumNetwork.SCROLL: "https://blockscout.scroll.io/graphiql",
        EthereumNetwork.ROOTSTOCK_MAINNET: "https://rootstock.blockscout.com/graphiql",
        EthereumNetwork.ROOTSTOCK_TESTNET: "https://rootstock-testnet.blockscout.com/graphiql",
        EthereumNetwork.LINEA: "https://explorer.linea.build/graphiql",
        EthereumNetwork.LINEA_TESTNET: "https://explorer.goerli.linea.build/graphiql",
        EthereumNetwork.NEON_EVM_MAINNET: "https://neon.blockscout.com/graphiql",
        EthereumNetwork.NEON_EVM_DEVNET: "https://neon-devnet.blockscout.com/graphiql",
        EthereumNetwork.OASIS_SAPPHIRE: "https://explorer.sapphire.oasis.io/graphiql",
        EthereumNetwork.OASIS_SAPPHIRE_TESTNET: "https://testnet.explorer.sapphire.oasis.dev/graphiql",
        EthereumNetwork.CASCADIA_TESTNET: "https://explorer.cascadia.foundation/graphiql",
        EthereumNetwork.TENET: "https://tenetscan.io/graphiql",
        EthereumNetwork.TENET_TESTNET: "https://testnet.tenetscan.io/graphiql",
        EthereumNetwork.VELAS_EVM_MAINNET: "https://evmexplorer.velas.com/graphiql",
        EthereumNetwork.CRONOS_MAINNET: "https://cronos.org/explorer/graphiql",
        EthereumNetwork.CRONOS_TESTNET: "https://cronos.org/explorer/testnet3/graphiql",
        EthereumNetwork.THUNDERCORE_MAINNET: "https://explorer-mainnet.thundercore.com/graphiql",
        EthereumNetwork.THUNDERCORE_TESTNET: "https://explorer-testnet.thundercore.com/graphiql",
        EthereumNetwork.PGN_PUBLIC_GOODS_NETWORK: "https://explorer.publicgoods.network/graphiql",
        EthereumNetwork.SEPOLIA_PGN_PUBLIC_GOODS_NETWORK: "https://explorer.sepolia.publicgoods.network/graphiql",
        EthereumNetwork.ARTHERA_MAINNET: "https://explorer.arthera.net/graphiql",
        EthereumNetwork.ARTHERA_TESTNET: "https://explorer-test.arthera.net/graphiql",
        EthereumNetwork.MANTA_PACIFIC_MAINNET: "https://pacific-explorer.manta.network/graphiql",
        EthereumNetwork.KROMA: "https://blockscout.kroma.network/graphiql",
        EthereumNetwork.KROMA_SEPOLIA: "https://blockscout.sepolia.kroma.network/graphiql",
        EthereumNetwork.ZORA: "https://explorer.zora.energy/graphiql",
        EthereumNetwork.ZORA_SEPOLIA_TESTNET: "https://sepolia.explorer.zora.energy/graphiql",
        EthereumNetwork.HAQQ_NETWORK: "https://explorer.haqq.network/graphiql",
        EthereumNetwork.HAQQ_CHAIN_TESTNET: "https://explorer.testedge2.haqq.network/graphiql",
        EthereumNetwork.MODE: "https://explorer.mode.network/graphiql",
        EthereumNetwork.MODE_TESTNET: "https://sepolia.explorer.mode.network/graphiql",
        EthereumNetwork.MANTLE_SEPOLIA_TESTNET: "https://explorer.sepolia.mantle.xyz/graphiql",
        EthereumNetwork.OP_SEPOLIA_TESTNET: "https://optimism-sepolia.blockscout.com/graphiql",
        EthereumNetwork.UNREAL_TESTNET: "https://unreal.blockscout.com/graphiql",
        EthereumNetwork.TAIKO_KATLA_L2: "https://explorer.katla.taiko.xyz/graphiql",
        EthereumNetwork.SEI_DEVNET: "https://seitrace.com/graphiql",
        EthereumNetwork.LISK_SEPOLIA_TESTNET: "https://sepolia-blockscout.lisk.com/graphiql",
        EthereumNetwork.MERLIN_MAINNET: "https://scan-v1.merlinchain.io/graphiql",
    }

    def __init__(self, network: EthereumNetwork):
        self.network = network
        self.grahpql_url = self.NETWORK_WITH_URL.get(network)
        if self.grahpql_url is None:
            raise BlockScoutConfigurationProblem(
                f"Network {network.name} - {network.value} not supported"
            )
        self.http_session = requests.Session()


class ContractMetadataService:
    def __init__(
        self, ethereum_client: EthereumClient, etherscan_api_key: Optional[str] = None
    ):
        self.ethereum_client = ethereum_client
        self.ethereum_network = ethereum_client.get_network()
        self.etherscan_api_key = etherscan_api_key
        self.etherscan_client = self._get_etherscan_client()
        self.blockscout_client = self._get_blockscout_client()
        self.sourcify_client = self._get_sourcify_client()
        self.enabled_clients = [
            client
            for client in (
                self.sourcify_client,
                self.etherscan_client,
                self.blockscout_client,
            )
            if client
        ]

    def _get_etherscan_client(self) -> Optional[EthereumClient]:
        try:
            return EtherscanClient(
                self.ethereum_network, api_key=self.etherscan_api_key
            )
        except EtherscanClientConfigurationProblem:
            logger.info(
                "Etherscan client is not available for current network %s",
                self.ethereum_network,
            )
            return None

    def _get_blockscout_client(self) -> Optional[BlockscoutClient]:
        try:
            return BlockscoutClient(self.ethereum_network)
        except BlockScoutConfigurationProblem:
            logger.info(
                "Blockscout client is not available for current network %s",
                self.ethereum_network,
            )
            return None

    def _get_sourcify_client(self) -> Optional[SourcifyClient]:
        try:
            return SourcifyClient(self.ethereum_network)
        except SourcifyClientConfigurationProblem:
            logger.info(
                "Sourcify client is not available for current network %s",
                self.ethereum_network,
            )
            return None

    def get_contract_metadata(
        self, contract_address: ChecksumAddress
    ) -> Optional[ContractMetadata]:
        """
        Get contract metadata from every enabled client

        :param contract_address: Contract address
        :return: Contract Metadata if found from any client, otherwise None
        """
        if contract_address in DEFAULT_ABI_MAP and DEFAULT_ABI_MAP[contract_address]:
            return DEFAULT_ABI_MAP[contract_address]
        for client in self.enabled_clients:
            try:
                contract_metadata = client.get_contract_metadata(contract_address)
                if contract_metadata:
                    return contract_metadata
            except IOError:
                logger.debug(
                    "Cannot get metadata for contract=%s on network=%s using client=%s",
                    contract_address,
                    self.ethereum_network.name,
                    client.__class__.__name__,
                )

        return None
