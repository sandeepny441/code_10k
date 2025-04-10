class Solution:
    def isAnagram(self, str_1: str, str_2: str) -> bool:
      # solution 1 -- two dicts
      dict_1 = {}
      for ch in str_1:
        if ch in dict_1:
          dict_1[ch] +=1
        else:
          dict_1[ch] = 1

      dict_2 = {}
      for ch in str_2:
        if ch in dict_2:
          dict_2[ch] +=1
        else:
          dict_2[ch] = 1

      return dict_1 == dict_2


      # solution 2 --  using Counter
      # from collections import Counter
      # return Counter(str_1) == Counter(str_2)

      # solution 3 -- suing sort
      # return sorted(str_1) == sorted(str_2)