import java.util.Random;
import java.util.TreeSet;

//Discard: Minimum Card
//Lead: Maximum Card
//Follow: Maximum Card
public class MinMaxBotHand extends Hand {
	protected static Random rng = new Random();
	
	public MinMaxBotHand(String n) {
		super(n);
	}
	
	public Card askDiscard() {
		return minCard(hand);
	}
	public Card askLead() {
		return maxCard(hand);
	}
	public Card askFollow(Card lead) {
		int followSuit = lead.getSuit();
		TreeSet<Card> choices = getSuitList(followSuit);
		if (choices.isEmpty()) {
			choices = hand;
		}
		return maxCard(choices);
	}
	private Card maxCard(Iterable<Card> choices) {
		Card maxCard = null;
		int max = 0;
		for (Card c : choices) {
			if (c.getRank() > max) {
				max = c.getRank();
				maxCard = c;
			}
		}
		return maxCard;
	}

	public boolean isHuman() {
		return false;
	}
	protected Card minCard(TreeSet<Card> choices) {
		Card minCard = null;
		int min = 15;
		for (Card c : choices) {
			if (c.getRank() < min) {
				min = c.getRank();
				minCard = c;
			}
		}
		return minCard;
	}

}