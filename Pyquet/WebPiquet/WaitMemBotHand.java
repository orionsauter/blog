import java.util.Random;
import java.util.TreeSet;

//Discard: Minimum Card
//Lead: Minimum card for first 4 tricks, then maximum card in last led suit unless greater card has not been seen
//Follow: Minimum Card that beats lead if possible, else minimum
public class WaitMemBotHand extends Hand {
	protected static Random rng = new Random();
	protected Card lastLead = null;
	private static TrickComp cmp = new TrickComp();
	private static final int wait = 5;
	
	public WaitMemBotHand(String n) {
		super(n);
	}
	
	public Card askDiscard() {
		return minCard(hand);
	}
	public Card askLead() {
		if (size() > wait) {
			return minCard(hand);
		}
		if (lastLead != null && hasSuit(lastLead.getSuit())) {
			lastLead =  maxCard(getSuitList(lastLead.getSuit()));
			if (existsBigger(lastLead)) {
				lastLead = maxCard(hand);
				if (existsBigger(lastLead)) {
					lastLead = minCard(hand);
				}
			}
		} else {
			lastLead = maxCard(hand);
			if (existsBigger(lastLead)) {
				lastLead = minCard(hand);
			}
		}
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
	private boolean existsBigger(Card test) {
		for (Card c :getUnseen()) {
			if (cmp.compare(test, c) < 0) {
				return true;
			}
		}
		return false;
	}

}