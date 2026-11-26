# The second look

cards/out/report.json lists cards drawn from a post's text. For every row with ok true whose id is not a key in cards/out/seen.json, open cards/out/<id>.jpg with the Read tool and compare it with the row's "text", word by word.

Write "ok" only if all of these are true:
1. Every word and every punctuation mark of the text is on the card, in order, and nothing else except the photo, Ayo Adesina and @ayo_deshina.
2. No letter is cut, overlapped or touching an edge, and no word is split across lines.
3. The photo is a clear face in a white ring, not blank or broken.
4. The text is bold, the ground is one flat blue, and the words are easy to read on it.
5. The English is correct. Two sentences joined by only a comma is a fail. Any mention of politics, religion, a client name, a price promise or an invented event is a fail.

Otherwise write "bad: " and the reason in under 15 words. Never write ok for a picture you did not open. Change only cards/out/seen.json.
