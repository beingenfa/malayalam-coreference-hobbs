from MalayalamCorefResolver import MalayalamCorefResolver


def main():
    resolver = MalayalamCorefResolver()

    examples = ["പൂച്ച മേശയ്‌ക്ക് മുകളിൽ ഇരിക്കുന്നു. അത് ഉറങ്ങുന്നു."]

    for doc in examples:
        print("=======================================")
        print("Document:", doc)

        result = resolver.find_coref(doc)

        tokens = result["tokens"]
        coref_results = result["coref"]

        if not coref_results:
            print("No pronoun resolutions found.\n")
            continue

        for sent_no, pron_dict in coref_results.items():
            for pron_idx, candidates in pron_dict.items():
                pronoun = tokens[sent_no][pron_idx]
                print(f"In Sentence {sent_no + 1}: '{pronoun}' → {candidates}")

if __name__ == "__main__":
    main()