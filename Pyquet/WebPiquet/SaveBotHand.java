import java.util.Random;
import java.util.TreeSet;

//Discard: Minimum Card unless needed for straight or tuple
//Lead: Random Card
//Follow: Random Card
public class SaveBotHand extends Hand {
	protected static Random rng = new Random();
	
	public SaveBotHand(String n) {
		super(n);
	}
	public Card askDiscard() {
		TreeSet<Card> choices = (TreeSet<Card>) hand.clone();
		int curTuple = maxTuple();
		int curStraight = straight();
		while (!choices.isEmpty()) {
			Card min = minCard(choices);
			hand.remove(min);
			choices.remove(min);
			if (min.getRank() > 11 || maxTuple() < curTuple || straight() < curStraight) {
				hand.add(min);
			} else {
				hand.add(min);
				return min;
			}
		}
		return minCard(hand);
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
