from charm.core.math.pairing import ZR
from charm.toolbox.policytree import *


class MSP:
    def __init__(self, groupObj, verbose=True):
        self.len_longest_row = 1
        self.group = groupObj

    def createPolicy(self, policy_string):
        assert type(policy_string) is str, "invalid type for policy_string"
        parser = PolicyParser()
        policy_obj = parser.parse(policy_string)
        _dictCount, _dictLabel = {}, {}
        parser.findDuplicates(policy_obj, _dictCount)
        for i in _dictCount.keys():
            if _dictCount[ i ] > 1: _dictLabel[ i ] = 0
        parser.labelDuplicates(policy_obj, _dictLabel)
        return policy_obj

    def convert_policy_to_msp(self, tree):
        root_vector = [1]
        self.len_longest_row = 1
        return self._convert_policy_to_msp(tree, root_vector)

    def _convert_policy_to_msp(self, subtree, curr_vector):
        if subtree is None:
            return None

        type = subtree.getNodeType()

        if type == OpType.ATTR:
            # print ('ATTR: ', subtree, subtree.getAttributeAndIndex(), currVector)
            return {subtree.getAttributeAndIndex(): curr_vector}

        if type == OpType.OR:
            left_list = self._convert_policy_to_msp(subtree.getLeft(), curr_vector)
            right_list = self._convert_policy_to_msp(subtree.getRight(), curr_vector)
            # print ('OR l: ', leftList, 'r: ', rightList)
            left_list.update(right_list)
            return left_list

        if type == OpType.AND:
            length = len(curr_vector)
            left_vector = curr_vector + [0] * (self.len_longest_row - length) + [1]
            right_vector = [0] * self.len_longest_row + [-1]  # [0]*k creates a vector of k zeroes
            # extendedVector = currVector + [0]*(self.lengthOfLongestRow-length)
            # leftVector = extendedVector + [1]
            # rightVector = extendedVector + [2]  # [0]*k creates a vector of k zeroes
            self.len_longest_row += 1
            left_list = self._convert_policy_to_msp(subtree.getLeft(), left_vector)
            right_list = self._convert_policy_to_msp(subtree.getRight(), right_vector)
            # print ('AND l: ', leftList, 'r: ', rightList)
            left_list.update(right_list)
            return left_list

        return None

    def getCoefficients(self, tree):
        coeffs = {}
        self._getCoefficientsDict(tree, coeffs)
        return coeffs

    def recoverCoefficients(self, list):
        coeff = {}
        list2 = [self.group.init(ZR, i) for i in list]
        for i in list2:
            result = 1
            for j in list2:
                if not (i == j):
                    # lagrange basis poly
                    result *= (0 - j) / (i - j)
                    #                print("coeff '%d' => '%s'" % (i, result))
            coeff[int(i)] = result
        return coeff

    def _getCoefficientsDict(self, tree, coeff_list, coeff=1):
        if tree:
            node = tree.getNodeType()
            if (node == OpType.AND):
                this_coeff = self.recoverCoefficients([1, 2])
                # left child => coeff[1], right child => coeff[2]
                self._getCoefficientsDict(tree.getLeft(), coeff_list, coeff * this_coeff[1])
                self._getCoefficientsDict(tree.getRight(), coeff_list, coeff * this_coeff[2])
            elif (node == OpType.OR):
                this_coeff = self.recoverCoefficients([1])
                self._getCoefficientsDict(tree.getLeft(), coeff_list, coeff * this_coeff[1])
                self._getCoefficientsDict(tree.getRight(), coeff_list, coeff * this_coeff[1])
            elif (node == OpType.ATTR):
                attr = tree.getAttributeAndIndex()
                coeff_list[attr] = coeff
            else:
                return None

    def strip_index(self, node_str):
        if node_str.find('_') != -1:
            return node_str.split('_')[0]
        return node_str

    def prune(self, policy, attributes):
        parser = PolicyParser()
        return parser.prune(policy, attributes)

    def getAttributeList(self, Node):
        aList = []
        self._getAttributeList(Node, aList)
        return aList

    def _getAttributeList(self, Node, List):
        if (Node == None):
            return None
        # V, L, R
        if (Node.getNodeType() == OpType.ATTR):
            List.append(Node.getAttributeAndIndex())  # .getAttribute()
        else:
            self._getAttributeList(Node.getLeft(), List)
            self._getAttributeList(Node.getRight(), List)
        return None
        
if __name__ == "__main__":
    util = MSP(ZR)
    kw_policy = '(1001:1 and 1002:2) or (1003:3 and 1004:4)'
    kw_policy = util.createPolicy(kw_policy) 
    
    print(kw_policy, type(kw_policy))
        
