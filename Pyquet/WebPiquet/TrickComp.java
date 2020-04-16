import java.util.Comparator;


public class TrickComp implements Comparator<Card> {

	public TrickComp() { }
	public int compare(Card lead, Card follow) {
		if (lead.getSuit() != follow.getSuit()) {
			return 1;
		} else {
			return (lead.getRank() - follow.getRank());
		}
	}

}
