from charm.toolbox.pairinggroup import PairingGroup, ZR, G1, G2, GT, pair
from charm.toolbox.ABEnc import ABEnc
from msp import MSP

debug = False


class KPABE(ABEnc):

    def __init__(self, group_obj, uni_size, verbose=False):
        ABEnc.__init__(self)
        self.name = "KP-ABE"
        self.group = group_obj
        self.uni_size = uni_size
        self.util = MSP(self.group, verbose)

    def setup(self):
        if debug:
            print('Setup algorithm:\n')
        g1 = self.group.random(G1)
        g2 = self.group.random(G2)
        alpha = self.group.random(ZR)
        e_gg_alpha = pair(g1, g2) ** alpha

        g_t = [1]
        t = [0]
        for i in range(self.uni_size):
            ti = self.group.random(ZR)
            t.append(ti)
            g_ti = g1 ** ti
            g_t.append(g_ti)

        pk = {'g_t': g_t, 'e_gg_alpha': e_gg_alpha}
        msk = {'g2': g2, 't': t, 'alpha': alpha}
        return pk, msk

    def encrypt(self, pk, msg, attr_list):
        if debug:
            print('Encryption algorithm:\n')

        s = self.group.random(ZR)
        c0 = pk['e_gg_alpha'] ** s * msg


        cy = {}
        for attr in attr_list:
            cy[attr] = pk['g_t'][int(attr)] ** s

        return {'attr_list': attr_list, 'c0': c0, 'cy': cy}

    def keygen(self, pk, msk, policy_str):
        if debug:
            print('Key generation algorithm:\n')

        policy = self.util.createPolicy(policy_str)
        mono_span_prog = self.util.convert_policy_to_msp(policy)
        num_cols = self.util.len_longest_row

        # pick randomness
        u = [msk['alpha']]
        for i in range(num_cols-1):
            rand = self.group.random(ZR)
            u.append(rand)

        k = {}
        for attr, row in mono_span_prog.items():
            cols = len(row)
            sum = 0
            for i in range(cols):
                sum += row[i] * u[i]
            attr_stripped = self.util.strip_index(attr)
            di = msk['g2'] ** (sum/msk['t'][int(attr_stripped)])
            k[attr] = di

        return {'policy': policy, 'k': k}

    def decrypt(self, pk, ctxt, key):
        if debug:
            print('Decryption algorithm:\n')

        nodes = self.util.prune(key['policy'], ctxt['attr_list'])
        if not nodes:
            print ("Policy not satisfied.")
            return None

        prodGT = 1

        for node in nodes:
            attr = node.getAttributeAndIndex()
            attr_stripped = self.util.strip_index(attr)
            prodGT *= pair(ctxt['cy'][attr_stripped],key['k'][attr])

        return (ctxt['c0'] / prodGT)
