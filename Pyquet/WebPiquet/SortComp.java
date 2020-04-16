import java.util.Comparator;


public class SortComp implements Comparator<Card> {
	public SortComp() { }
	public int compare(Card a, Card b) {
		if (a.getSuit() != b.getSuit()) {
			return a.getSuit() - b.getSuit();
		} else {
			return a.getRank() - b.getRank();
		}
	}
}
