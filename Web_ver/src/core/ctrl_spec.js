// Generated from the Python __ctrl__.py tbl_nci_ctrl tables (handler names only).
// Regenerate with: python scripts/gen_ctrl_spec.py

export const CTRL_FORUM20 = {
  "NCI Core": {
    "00": {
      "CMD": "CORE_RESET_CMD",
      "RSP": "CORE_RESET_RSP",
      "NTF": "CORE_RESET_NTF"
    },
    "01": {
      "CMD": "CORE_INIT_CMD",
      "RSP": "CORE_INIT_RSP"
    },
    "02": {
      "CMD": "CORE_SET_CONFIG_CMD",
      "RSP": "CORE_SET_CONFIG_RSP"
    },
    "03": {
      "CMD": "CORE_GET_CONFIG_CMD",
      "RSP": "CORE_GET_CONFIG_RSP"
    },
    "04": {
      "CMD": "CORE_CONN_CREATE_CMD",
      "RSP": "CORE_CONN_CREATE_RSP"
    },
    "05": {
      "CMD": "CORE_CONN_CLOSE_CMD",
      "RSP": "CORE_CONN_CLOSE_RSP"
    },
    "06": {
      "NTF": "CORE_CONN_CREDITS_NTF"
    },
    "07": {
      "NTF": "CORE_GENERIC_ERROR_NTF"
    },
    "08": {
      "NTF": "CORE_INTERFACE_ERROR_NTF"
    },
    "09": {
      "CMD": "CORE_SET_POWER_SUB_STATE_CMD",
      "RSP": "CORE_SET_POWER_SUB_STATE_RSP"
    }
  },
  "RF Management": {
    "00": {
      "CMD": "RF_DISCOVER_MAP_CMD",
      "RSP": "RF_DISCOVER_MAP_RSP"
    },
    "01": {
      "CMD": "RF_SET_LISTEN_MODE_ROUTING_CMD",
      "RSP": "RF_SET_LISTEN_MODE_ROUTING_RSP"
    },
    "02": {
      "CMD": "RF_GET_LISTEN_MODE_ROUTING_CMD",
      "RSP": "RF_GET_LISTEN_MODE_ROUTING_RSP",
      "NTF": "RF_GET_LISTEN_MODE_ROUTING_NTF"
    },
    "03": {
      "CMD": "RF_DISCOVER_CMD",
      "RSP": "RF_DISCOVER_RSP",
      "NTF": "RF_DISCOVER_NTF"
    },
    "04": {
      "CMD": "RF_DISCOVER_SELECT_CMD",
      "RSP": "RF_DISCOVER_SELECT_RSP"
    },
    "05": {
      "NTF": "RF_INTF_ACTIVATED_NTF"
    },
    "06": {
      "CMD": "RF_DEACTIVATE_CMD",
      "RSP": "RF_DEACTIVATE_RSP",
      "NTF": "RF_DEACTIVATE_NTF"
    },
    "07": {
      "NTF": "RF_FIELD_INFO_NTF"
    },
    "08": {
      "CMD": "RF_T3T_POLLING_CMD",
      "RSP": "RF_T3T_POLLING_RSP",
      "NTF": "RF_T3T_POLLING_NTF"
    },
    "09": {
      "NTF": "RF_NFCEE_ACTION_NTF"
    },
    "0A": {
      "NTF": "RF_NFCEE_DISCOVERY_REQ_NTF"
    },
    "0B": {
      "CMD": "RF_PARAMETER_UPDATE_CMD",
      "RSP": "RF_PARAMETER_UPDATE_RSP"
    },
    "0C": {
      "CMD": "RF_INTF_EXT_START_CMD",
      "RSP": "RF_INTF_EXT_START_RSP"
    },
    "0D": {
      "CMD": "RF_INTF_EXT_STOP_CMD",
      "RSP": "RF_INTF_EXT_STOP_RSP"
    },
    "0E": {
      "CMD": "RF_EXT_AGG_ABORT_CMD",
      "RSP": "RF_EXT_AGG_ABORT_RSP"
    },
    "0F": {
      "CMD": "RF_NDEF_ABORT_CMD",
      "RSP": "RF_NDEF_ABORT_RSP"
    },
    "10": {
      "CMD": "RF_ISO_DEP_NAK_PRESENCE_CMD",
      "RSP": "RF_ISO_DEP_NAK_PRESENCE_RSP",
      "NTF": "RF_ISO_DEP_NAK_PRESENCE_NTF"
    },
    "11": {
      "CMD": "RF_SET_FORCED_NFCEE_ROUTING_CMD",
      "RSP": "RF_SET_FORCED_NFCEE_ROUTING_RSP"
    }
  },
  "NFCEE Management": {
    "00": {
      "CMD": "NFCEE_DISCOVER_CMD",
      "RSP": "NFCEE_DISCOVER_RSP",
      "NTF": "NFCEE_DISCOVER_NTF"
    },
    "01": {
      "CMD": "NFCEE_MODE_SET_CMD",
      "RSP": "NFCEE_MODE_SET_RSP",
      "NTF": "NFCEE_MODE_SET_NTF"
    },
    "02": {
      "NTF": "NFCEE_STATUS_NTF"
    },
    "03": {
      "CMD": "NFCEE_POWER_AND_LINK_CNTRL_CMD",
      "RSP": "NFCEE_POWER_AND_LINK_CNTRL_RSP"
    }
  }
};

export const CTRL_NXP = {
  "NCI Core": {
    "00": {
      "CMD": "CORE_RESET_CMD",
      "RSP": "CORE_RESET_RSP",
      "NTF": "CORE_RESET_NTF"
    },
    "01": {
      "CMD": "CORE_INIT_CMD",
      "RSP": "CORE_INIT_RSP"
    },
    "02": {
      "CMD": "CORE_SET_CONFIG_CMD",
      "RSP": "CORE_SET_CONFIG_RSP"
    },
    "03": {
      "CMD": "CORE_GET_CONFIG_CMD",
      "RSP": "CORE_GET_CONFIG_RSP"
    },
    "04": {
      "CMD": "CORE_CONN_CREATE_CMD",
      "RSP": "CORE_CONN_CREATE_RSP"
    },
    "05": {
      "CMD": "CORE_CONN_CLOSE_CMD",
      "RSP": "CORE_CONN_CLOSE_RSP"
    },
    "06": {
      "NTF": "CORE_CONN_CREDITS_NTF"
    },
    "07": {
      "NTF": "CORE_GENERIC_ERROR_NTF"
    },
    "08": {
      "NTF": "CORE_INTERFACE_ERROR_NTF"
    },
    "09": {
      "CMD": "CORE_SET_POWER_SUB_STATE_CMD",
      "RSP": "CORE_SET_POWER_SUB_STATE_RSP"
    }
  },
  "RF Management": {
    "00": {
      "CMD": "RF_DISCOVER_MAP_CMD",
      "RSP": "RF_DISCOVER_MAP_RSP"
    },
    "01": {
      "CMD": "RF_SET_LISTEN_MODE_ROUTING_CMD",
      "RSP": "RF_SET_LISTEN_MODE_ROUTING_RSP"
    },
    "02": {
      "CMD": "RF_GET_LISTEN_MODE_ROUTING_CMD",
      "RSP": "RF_GET_LISTEN_MODE_ROUTING_RSP",
      "NTF": "RF_GET_LISTEN_MODE_ROUTING_NTF"
    },
    "03": {
      "CMD": "RF_DISCOVER_CMD",
      "RSP": "RF_DISCOVER_RSP",
      "NTF": "RF_DISCOVER_NTF"
    },
    "04": {
      "CMD": "RF_DISCOVER_SELECT_CMD",
      "RSP": "RF_DISCOVER_SELECT_RSP"
    },
    "05": {
      "NTF": "RF_INTF_ACTIVATED_NTF"
    },
    "06": {
      "CMD": "RF_DEACTIVATE_CMD",
      "RSP": "RF_DEACTIVATE_RSP",
      "NTF": "RF_DEACTIVATE_NTF"
    },
    "07": {
      "NTF": "RF_FIELD_INFO_NTF"
    },
    "08": {
      "CMD": "RF_T3T_POLLING_CMD",
      "RSP": "RF_T3T_POLLING_RSP",
      "NTF": "RF_T3T_POLLING_NTF"
    },
    "09": {
      "NTF": "RF_NFCEE_ACTION_NTF"
    },
    "0A": {
      "NTF": "RF_NFCEE_DISCOVERY_REQ_NTF"
    },
    "0B": {
      "CMD": "RF_PARAMETER_UPDATE_CMD",
      "RSP": "RF_PARAMETER_UPDATE_RSP"
    },
    "0C": {
      "CMD": "RF_INTF_EXT_START_CMD",
      "RSP": "RF_INTF_EXT_START_RSP"
    },
    "0D": {
      "CMD": "RF_INTF_EXT_STOP_CMD",
      "RSP": "RF_INTF_EXT_STOP_RSP"
    },
    "0E": {
      "CMD": "RF_EXT_AGG_ABORT_CMD",
      "RSP": "RF_EXT_AGG_ABORT_RSP"
    },
    "0F": {
      "CMD": "RF_NDEF_ABORT_CMD",
      "RSP": "RF_NDEF_ABORT_RSP"
    },
    "10": {
      "CMD": "RF_ISO_DEP_NAK_PRESENCE_CMD",
      "RSP": "RF_ISO_DEP_NAK_PRESENCE_RSP",
      "NTF": "RF_ISO_DEP_NAK_PRESENCE_NTF"
    },
    "11": {
      "CMD": "RF_SET_FORCED_NFCEE_ROUTING_CMD",
      "RSP": "RF_SET_FORCED_NFCEE_ROUTING_RSP"
    },
    "18": {
      "NTF": "IOT_RETRY_NTF"
    },
    "20": {
      "NTF": "FIELD_DETECT_NTF"
    },
    "21": {
      "NTF": "PLL_UNLOCKED_NTF"
    },
    "23": {
      "NTF": "TxLDO_ERROR_NTF"
    },
    "28": {
      "NTF": "PLL_LOSTLOCK_NTF"
    },
    "29": {
      "NTF": "SETTINGS_CHANGE_NTF"
    },
    "2A": {
      "NTF": "RF_FREQ_ERROR_NTF"
    },
    "2B": {
      "NTF": "LPDET_ERROR_NTF"
    }
  },
  "NFCEE Management": {
    "00": {
      "CMD": "NFCEE_DISCOVER_CMD",
      "RSP": "NFCEE_DISCOVER_RSP",
      "NTF": "NFCEE_DISCOVER_NTF"
    },
    "01": {
      "CMD": "NFCEE_MODE_SET_CMD",
      "RSP": "NFCEE_MODE_SET_RSP",
      "NTF": "NFCEE_MODE_SET_NTF"
    },
    "02": {
      "NTF": "NFCEE_STATUS_NTF"
    },
    "03": {
      "CMD": "NFCEE_POWER_AND_LINK_CNTRL_CMD",
      "RSP": "NFCEE_POWER_AND_LINK_CNTRL_RSP"
    }
  },
  "Proprietary": {
    "00": {
      "CMD": "CORE_SET_POWER_MODE_CMD",
      "RSP": "CORE_SET_POWER_MODE_RSP"
    },
    "01": {
      "CMD": "SET_NFC_SERVICE_STATUS_CMD",
      "RSP": "SET_NFC_SERVICE_STATUS_RSP"
    },
    "02": {
      "CMD": "NCI_PROPRIETARY_ACT_CMD",
      "RSP": "NCI_PROPRIETARY_ACT_RSP"
    },
    "04": {
      "NTF": "APDU_LOGGING_NTF"
    },
    "14": {
      "CMD": "RF_GET_TRANSITION_CMD",
      "RSP": "RF_GET_TRANSITION_RSP"
    },
    "17": {
      "NTF": "WTX_NTF"
    },
    "1C": {
      "CMD": "LOW_POWER_TAG_REMOVAL_CMD",
      "RSP": "LOW_POWER_TAG_REMOVAL_RSP",
      "NTF": "LOW_POWER_TAG_REMOVAL_NTF"
    },
    "1E": {
      "CMD": "SYSTEM_ESE_POWER_CYCLE_CMD",
      "RSP": "SYSTEM_ESE_POWER_CYCLE_RSP"
    },
    "1F": {
      "CMD": "COLD_RESET_CMD",
      "RSP": "COLD_RESET_RSP",
      "NTF": "COLD_RESET_NTF"
    },
    "21": {
      "CMD": "FLUSH_SRAM_AO_TO_FLASH_CMD",
      "RSP": "FLUSH_SRAM_AO_TO_FLASH_RSP"
    },
    "30": {
      "CMD": "TEST_PRBS_CMD",
      "RSP": "TEST_PRBS_RSP"
    },
    "32": {
      "CMD": "READ_OPTION_CMD",
      "RSP": "READ_OPTION_RSP"
    },
    "33": {
      "CMD": "TEST_PRBS_CARD_CMD",
      "RSP": "TEST_PRBS_CARD_RSP"
    },
    "35": {
      "NTF": "L1_DEBUG_NTF"
    },
    "36": {
      "NTF": "L2_DEBUG_NTF"
    },
    "3D": {
      "CMD": "RF_SPC_CMD",
      "RSP": "RF_SPC_RSP",
      "NTF": "RF_SPC_NTF"
    },
    "3E": {
      "CMD": "TEST_SWP_CMD",
      "RSP": "TEST_SWP_RSP",
      "NTF": "TEST_SWP_NTF"
    },
    "3F": {
      "CMD": "OPTIONAL_CMD",
      "RSP": "OPTIONAL_RSP"
    }
  },
  "HDLL": {
    "F0": "DL_RESET",
    "F1": "DL_GET_VERSION",
    "F2": "DL_GET_SESSION_STATE",
    "F4": "DL_GET_DIE_ID",
    "E0": "DL_CHECK_INTEGRITY",
    "C0": "DL_SEC_WRITE",
    "C1": "DL_CERT_FRAME",
    "00": "DL_OK",
    "01": "EDL_INVALID_ADDR",
    "02": "EDL_GENERIC_ERROR",
    "0B": "EDL_UNKNOW_CMD",
    "0C": "EDL_ABORTED_CMD",
    "1E": "EDL_ADDR_RANGE_OFL_ERROR",
    "1F": "EDL_BUFFER_OFL_ERROR",
    "20": "EDL_MEM_BSY",
    "21": "EDL_SIGNATURE_ERROR",
    "24": "EDL_FIRMWARE_VERSION_ERROR",
    "28": "EDL_PROTOCOL_ERROR",
    "2D": "PH_STATUS_DL_FIRST_CHUNK",
    "2E": "PH_STATUS_DL_NEXT_CHUNK",
    "31": "PH_STATUS_EDL_CERT_ERROR"
  }
};
