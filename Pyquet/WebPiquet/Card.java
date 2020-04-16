
public class Card {
	protected String name;
	protected int rank;
	protected int suit;

	public Card(int r, int s) {
		rank = r;
		suit = s;
		name = "";
		if (rank == 11) {
			name += "J";
		} else if (rank == 12) {
			name += "Q";
		} else if (rank == 13) {
			name += "K";
		} else if (rank == 14 || rank == 1) {
			name += "A";
		} else {
			name += rank;
		}
		if (suit == 0) {
			name += "D";
		} else if (suit == 1) {
			name += "C";
		} else if (suit == 2) {
			name += "H";
		} else {
			name += "S";
		}
	}

	public int getRank() { return rank; }
	public int getSuit() { return suit; }
	public String toString() { return name; }
	public boolean equals(Card c) {
		if (c == null) { return false; }
		return (c.getRank() == rank && c.getSuit() == suit);
	}
}
