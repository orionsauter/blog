import java.util.LinkedList;
import java.util.Random;
import java.util.TreeSet;

//Discard: Minimum Card unless needed for straight or tuple
//Lead: Maximum card if has at least two winning cards in suit, else minimum card
//Follow: Minimum Card that beats lead if possible, else minimum
public class MemoryBotHand extends Hand {
	protected static Random rng = new Random();
	protected Card lastLead = null;
	private static TrickComp cmp = new TrickComp();
	
	public MemoryBotHand(String n) {
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
		if (lastLead != null && hasSuit(lastLead.getSuit()) && !existsBigger(maxCard(getSuitList(lastLead.getSuit())))) {
			lastLead =  maxCard(getSuitList(lastLead.getSuit()));
		} else {
			lastLead = maxCard(leadSuit());
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
		if (choices == null) return null;
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
		if (test == null) return true;
		for (Card c :getUnseen()) {
			if (cmp.compare(test, c) < 0) {
				return true;
			}
		}
		return false;
	}
	private TreeSet<Card> leadSuit() {
		for (int i = 0; i < 4; i++) {
			TreeSet<Card> suit = getSuitList(i);
			if (topStraight(suit)) {
				return suit;
			}
		}
		return null;
	}
	private boolean topStraight(TreeSet<Card> suit) {
		if (suit.isEmpty()) return false;
		LinkedList<Card> list = new LinkedList<Card>();
		for (Card c : suit) {
			list.add(0, c);
		}
		int count = 0;
		for (Card c : list) {
			if (existsBigger(c)) {
				return false;
			}
			count++;
			if (count > 1) {
				return true;
			}
		}
		return true;
	}
	public void clear() {
		tricks = 0;
		lastLead = null;
		hand.clear();
	}

}