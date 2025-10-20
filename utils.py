
import hashlib

def palindrom(word: str) -> bool:
	if len(word) == 0 or len(word) == 1:
		return True
		
	elif word[0]  == word[-1]:
		return palindrom(word[1:-1])
				
	return False


def num_words(phrase: str) -> int:
    word_list =  phrase.split(" ")
    return len(word_list)


def num_unique_cha(phrase: str) -> int:
    unique_chars = set(phrase)
    return len(unique_chars)

def freq_chars(phrase: str) -> dict:
    freq = {char: phrase.count(char) for char in set(phrase)}
    return freq

def hash_word(phrase: str) -> str:
    return hashlib.sha256(phrase.encode()).hexdigest()
