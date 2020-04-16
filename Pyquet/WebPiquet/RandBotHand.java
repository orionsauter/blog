import java.util.Random;
import java.util.TreeSet;

// Discard: Random Card
// Lead: Random Card
// Follow: Random Card
public class RandBotHand extends Hand {
	protected static Random rng = new Random();
	
	public RandBotHand(String n) {
		super(n);
	}
	public Card askDiscard() {
		int i = rng.nextInt(size());
		return getIndex(i);
	}
	public Card askLead() {
		int i = rng.nextInt(size());
		return getIndex(i);
	}
	public Card askFollow(Card lead) {
		int followSuit = lead.getSuit();
		TreeSet<Card> choices = getSuitList(followSuit);
		if (choices.isEmpty()) {
			choices = hand;
		}
		int index = rng.nextInt(choices.size());
		int i = 0;
		for (Card c : choices) {
			if (i == index) {
				return c;
			}
			i++;
		}
		return null;
	}
	public boolean isHuman() {
		return false;
	}
}
