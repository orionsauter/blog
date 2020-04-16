import java.util.ArrayList;


public class Pile {
	protected ArrayList<Card> pile;
	protected String name;

	public Pile(String n) {
		pile = new ArrayList<Card>();
		name = n;
	}

	public void addCard(Card c) {
		pile.add(0, c);
	}
	public Card takeCard(int index) {
		return pile.remove(index);
	}
	public int size() {
		return pile.size();
	}
	public String toString() {
		String out = name + ": ";
		for (Card card: pile) {
			out += (card + " ");
		}
		return out;
	}
	public ArrayList<Card> getPile() {
		return pile;
	}
}
