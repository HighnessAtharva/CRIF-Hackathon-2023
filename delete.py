with open('negative_words.txt', 'r', encoding='utf-8') as file:
    negative_words = file.read().splitlines()
with open('bad_words.txt', 'r', encoding='utf-8') as file:
    bad_words = file.read().splitlines()

for word in bad_words:
    if word in negative_words:
        negative_words.remove(word)

print(len(bad_words))
print(len(negative_words))

with open("negative_words_new.txt", "w", encoding='utf-8') as file:
    file.write("\n".join(negative_words))
    
    
