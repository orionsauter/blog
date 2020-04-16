import java.util.Random;
import java.util.TreeSet;

//Discard: Minimum Card
//Lead: Random Card
//Follow: Random Card
public class MinBotHand extends Hand {
	protected static Random rng = new Random();
	
	public MinBotHand(String n) {
		super(n);
	}
	public Card askDiscard() {
		return minCard();
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
	protected Card minCard() {
		Card minCard = null;
		int min = 15;
		for (Card c : hand) {
			if (c.getRank() < min) {
				min = c.getRank();
				minCard = c;
			}
		}
		return minCard;
	}

}
