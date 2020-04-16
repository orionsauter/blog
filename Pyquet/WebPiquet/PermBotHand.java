import java.util.LinkedList;
import java.util.Random;
import java.util.TreeSet;

//Discard: Minimum Card unless needed for straight or tuple
//Lead & Follow: Card which maximizes winning outcomes in the next 3 tricks
public class PermBotHand extends Hand {
	protected static Random rng = new Random();
	protected Card lastLead = null;
	private static TrickComp cmp = new TrickComp();
	private GameTree tree;
	
	public PermBotHand(String n) {
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
		if (tree == null) {
			tree = new GameTree(this, getOpponent(), null);
			tree.buildTree();
		}
		Card best = tree.findBest(hand);
		tree.setPos(best);
		return best;
	}
	public Card askFollow(Card lead) {
		if (tree == null) {
			tree = new GameTree(this, getOpponent(), lead);
			tree.buildTree();
		}
		TreeSet<Card> choices = getSuitList(lead.getSuit());
		if (choices.isEmpty()) { choices = hand; }
		Card best = tree.findBest(choices);
		tree.setPos(best);
		return best;
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
		tree = null;
		hand.clear();
	}
	public void markSeen(Card c) {
		if (tree == null) {
			tree = new GameTree(this, getOpponent(), c);
			tree.buildTree();
			super.markSeen(c);
			return;
		}
		tree.setPos(c);
		super.markSeen(c);
	}
	public boolean addCard(Card c) {
		return hand.add(c);
	}

}