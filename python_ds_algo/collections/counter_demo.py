from collections import Counter

def is_anagram(s1, s2):
    # O(n) frequency comparison
    return Counter(s1) == Counter(s2)

# Test cases
words = [("listen", "silent"), ("apple", "pale"), ("earth", "heart")]
for w1, w2 in words:
    result = is_anagram(w1, w2)
    print(f"Are '{w1}' and '{w2}' anagrams? {result}")
