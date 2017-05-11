import binascii, os, struct, sys
from pcapfile import savefile

def get_little_endian_bytestring(bytestring, begin, end):
    s = ''
    for i in range(end - 1, begin - 1, -1):
        s += bytestring[i]

    return s

def get_ble_section(pkt, section, ppi_hdr = True):
    valid_sections = ['preamble', 'acc_addr', 'pdu_hdr', 'pdu', 'pdu_body',
                      'l2_hdr', 'l2', 'l2_body', 'att_op', 'payload', 'mic',
                      'crc']
    if section not in valid_sections:
        return None

    len_payload = len(pkt.raw()) - 19

    # array indexes that are passed to get_little_endian_bytestring
    format = dict()
    format['preamble'] = (0, 1)
    format['acc_addr'] = (1, 5)

    format['pdu_hdr'] = (5, 7)
    format['pdu'] = (5, len(pkt.raw()) - 7)
    format['pdu_body'] = (7, len(pkt.raw()) - 7)

    format['l2_hdr'] = (7, 11)
    format['l2'] = (7, len(pkt.raw()) - 7)
    format['l2_body'] = (11, len(pkt.raw()) - 7)

    format['att_op'] = (11, 12)
    format['payload'] = (12, len(pkt.raw()) - 7)

    format['mic'] = (len(pkt.raw()) - 7, len(pkt.raw()) - 3)
    format['crc'] = (len(pkt.raw()) - 3, len(pkt.raw()))

    begin, end = format[section]
    # if ppi header is present, the actual ble packet contents are offset
    if ppi_hdr:
        begin += 24
        end += 24

    # print 'beginning, end of section {2} = {0}, {1}'.format(begin, end, section)
    # print 'packet length: {0}'.format(len(pkt.raw()))
    return get_little_endian_bytestring(pkt.raw(), begin, end)

def main():
    # takes a pcap file as its only argument
    if len(sys.argv) != 2:
        print 'Usage: python2 btle-parse.py <pcap>'
        print 'Try me out with a sample pcap file! Run \'python2 btle-parse.py crackle-sample/decrypted.pcap\''
        sys.exit(1)

    testcap = open(sys.argv[1], 'rb')
    cap = savefile.load_savefile(testcap, verbose=True)

    # filter connections by access address into separate conversations
    print
    print 'Filtering by access address...'
    convos = dict()
    for pkt in cap.packets:
        # find access address (the first four bytes), but need an offset
        # because the first 24 bytes is the PPI header
        aa = get_little_endian_bytestring(pkt.raw(), 24, 28)

        # create a list of packets were sent with that access address
        if aa not in convos:
            convos[aa] = list()
        convos[aa].append(pkt)

    # find access address 0x8e89bed6 (advertising packets) and print stats
    unique = len(convos.keys())
    adv_aa = '\x8e\x89\xbe\xd6'
    if adv_aa in convos.keys():
        unique -= 1
        num_adv_ind = 0
        connect_req_found = False
        adv_pkts = convos[adv_aa]
        for pkt in adv_pkts:
            # find number of ADV_IND (connectable undirected advertising) pkts
            pdu_type = get_little_endian_bytestring(pkt.raw(), 28, 29)
            if pdu_type == '\x00':
                num_adv_ind += 1
            # get pdu header
            pdu_hdr = get_little_endian_bytestring(pkt.raw(), 28, 30)
            # if the least significant 4 bits are 0b0101, it's a CONNECT_REQ
            if (int(binascii.hexlify(pdu_hdr), 16) & 0x05) == 0x05:
                connect_req_found = True

        print '{0} ADV_IND (connectable undirected advertising) packets found'.format(num_adv_ind)
        print '{0} other types of advertising packets found'.format(len(adv_pkts) - num_adv_ind)
        if connect_req_found:
            print '\tsaw CONNECT_REQ; the two devices were communicating'
        print

    print '{0} unique conversations found'.format(unique)
    print


    # print stats about non-advertising packets
    for aa in convos.keys():
        if aa == adv_aa:
            continue

        pkts = convos[aa]

        print 'Conversation with access address {0}:'.format('0x' + binascii.hexlify(aa))
        print '\tTotal number of packets: {0}'.format(len(pkts))

        # find number of empty packets
        num_empty = num_ctrl = 0
        ll_enc_req_found = ll_enc_rsp_found = ll_start_enc_req_found = False
        for pkt in pkts:
            if len(pkt.raw()) <= 33:
                num_empty += 1
            else:
                # get packet header
                pdu_hdr = get_little_endian_bytestring(pkt.raw(), 28, 30)

                # if the two least significant bits are 11, it's a ctrl packet
                if int(binascii.hexlify(pdu_hdr), 16) & 0x03 == 0x03:
                    num_ctrl += 1
                    ctrl_opcode = get_little_endian_bytestring(pkt.raw(), 30, 31)
                    # LL_ENC_REQ: the next byte is 0x03
                    if int(binascii.hexlify(ctrl_opcode), 16) & 0x03 == 0x03:
                        ll_enc_req_found = True
                    # LL_ENC_RSP: the next byte is 0x04
                    if int(binascii.hexlify(ctrl_opcode), 16) & 0x04 == 0x04:
                        ll_enc_rsp_found = True
                    # LL_START_ENC_REQ: the next byte is 0x05
                    if int(binascii.hexlify(ctrl_opcode), 16) & 0x05 == 0x05:
                        ll_start_enc_req_found = True

        print '\t{0} empty packets'.format(num_empty)
        print '\t{0} control packets'.format(num_ctrl)
        print '\t{0} data packets'.format(len(pkts) - num_empty - num_ctrl)
        if ll_enc_req_found and ll_enc_rsp_found and ll_start_enc_req_found:
            print '\tConversation used encryption'
        print

if __name__ == '__main__':
    main()
