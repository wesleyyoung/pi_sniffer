class DisplayService:

    @staticmethod
    def get_paragraph(width, height, string, break_words=False):
        vendor_words = string.split(" ")
        chunks = []
        word_index = 0
        for word in vendor_words:
            try:
                existing_chunk = chunks[word_index]
                if existing_chunk:
                    if len(existing_chunk + word) >= width:
                        word_index += 1
                        chunks.append(word[:width])
                        if break_words and len(word) > (width + 1):
                            chunks.append(word[width:] + ' ')
                            word_index += 1
                    else:
                        chunks[word_index] = chunks[word_index] + ' ' + word
                else:
                    chunks.append(word[:width])
            except:
                chunks.append(word[:width])
                if break_words and len(word) > (width + 1):
                    chunks.append(word[width:] + ' ')
                    word_index += 1

        return chunks[:height]