import java.util.Random;
import java.util.TreeSet;

//Discard: Minimum Card
//Lead: Maximum Card in last led suit
//Follow: Minimum Card that beats lead if possible, else minimum
public class RunBotHand extends Hand {
	protected static Random rng = new Random();
	protected Card lastLead = null;
	private static TrickComp cmp = new TrickComp();
	
	public RunBotHand(String n) {
		super(n);
	}
	
	public Card askDiscard() {
		return minCard(hand);
	}
	public Card askLead() {
		if (lastLead != null && hasSuit(lastLead.getSuit())) {
			lastLead =  maxCard(getSuitList(lastLead.getSuit()));
			return lastLead;
		}
		lastLead = maxCard(hand);
		return lastLead;
	}
	public Card askFollow(Card lead) {
		lastLead = null;
		int followSuit = lead.getSuit();
		TreeSet<Card> choices = getSuitList(followSuit);
		if (choices.isEmpty()) {
			choices = hand;
		}
		Card followCard = beatCardWith(lead, choices);
		if (followCard != null) {
			return followCard;
		} else {
			return minCard(choices);
		}
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
	private Card beatCardWith(Card leadCard, TreeSet<Card> choices) {
		for (Card c : choices) {
			if (cmp.compare(leadCard, c) < 0) {
				return c;
			}
		}
		return null;
	}

}