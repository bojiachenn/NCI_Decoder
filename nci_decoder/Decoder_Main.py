import importlib

import vendor_registry


def NFC_NCI_DECODER(len, string, vendor, model, mode):
	pkg = importlib.import_module(vendor_registry.resolve(vendor).ctrl_module)

	# Message Type
	tbl_mt_val = {
		"000":	"DATA",
		"001":	"CMD",
		"010":	"RSP",
		"011":	"NTF",
	}

	#table 139
	tbl_gid_val = {
		"0000":	"NCI Core",
		"0001":	"RF Management",
		"0010":	"NFCEE Management",
		"0011":	"NFCC Management",
		"0100":	"Test Management",
		"1111":	"Proprietary",
	}

	raw = string.replace(" ", "")
	raw = raw.upper()
	# print("")
	first_oct_hex = raw[0:2]
	first_oct_b = bin(int(first_oct_hex,16))[2::].zfill(8)
	mt_val = tbl_mt_val.get(first_oct_b[0:3],"RFU")
	pbf = first_oct_b[3:4]

	payload_len = raw[4:6]

	# if(mt_val == "RFU"):
	# 	print("* NCI: RFU Data")
	# 	print("")
	if(int(payload_len, 16) == int(len)-3): # 3 Bytes header
		if(mt_val == "DATA" and bin(int(raw[2:4],16))[2::].zfill(8)[:6] == "000000"):
			print("  << NCI: DATA Packet >>  ", end="")
			if(mode == 1):
				print(raw)
			else:
				print("")
			conn_id = first_oct_b[4::]
			cr = bin(int(raw[2:4],16))[2::].zfill(8)[6::]
			print("  * Conn ID:", int(conn_id, 2), end=' ')
			if(conn_id == "0000"): 
				print("(Static: DH -- Remote NFC Endpoint)")
			elif(conn_id == "0001"): 
				print("(Static: DH -- HCI Network)")
			else: 
				print("(Dynamically assigned)")
			print("  * Credits:", int(cr, 2))
			print("  * Payload Length:", int(payload_len,16))
			print("  * data:", raw[6::])
			# Data 封包也有格式需要解析 之後做~~
			# print("")
			if((int(len)-3) != int(payload_len,16)):
				print("Error: Payload error!!")
				print("  Packet Len:", len, "Octet(s)")
				print("  Payload Len:", int(payload_len,16), "Octet(s)")

		else:   # Control Packet
			gid_val = tbl_gid_val.get(first_oct_b[4::]) # GID
			oid = raw[2:4] # OID
			# if(gid_val != "Proprietary"):
			try:
				function = f"{pkg.tbl_nci_ctrl[gid_val][oid][mt_val]}"
				function_name = function.split(" ")[1]
			except KeyError:
				print("  << ERROR_NOT_FOUND >>  ", end="")
				if(mode == 1):
					print(raw)
				else:
					print("")
				raise
			print("  << "+function_name+" >>  ", end="")
			if(mode == 1):
				print(raw)
			else:
				print("")
			# print("  * Payload Length:", int(payload_len,16))
			check = pkg.tbl_nci_ctrl[gid_val][oid][mt_val](raw[6::]) # 呼叫對應func，輸入rawdata

			if(check != 2*(int(len)-3)):
				print("Error: Payload error!!")
				print("  Packet Len:", len, "Octet(s)")
				print("  Payload Len:", int(payload_len,16), "Octet(s)")
				print("  Check Len:", check/2, "Octet(s)")
		if(pbf == "1"):
			print("PBF: "+pbf)
		print("#end")

	elif(int(first_oct_b[3:] + bin(int(raw[2:4],16))[2::].zfill(8), 2) == int(len)-4): # 2 Bytes header (HDLL) + CRC16 (2 Bytes)
		 # Nxp: Host Data Link Layer (HDLL)
		pkg.HDLL(raw, mode)

	else:
		print("Error: Unknown raw data!")
	

# def main():
# 	raw = input("Input the NCI raw data: ")
# 	NFC_NCI_DECODER(raw)

# if __name__ == '__main__':
# 	main()