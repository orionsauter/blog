import java.util.HashMap;
import java.util.TreeSet;


public class GTNode {
	private Hand player;
	private Hand oppon;
	private boolean pTurn;
	private boolean complete;
	private GTNode parent;
	private Card parentCard;
	private int branchScore;
	private int depth;
	private HashMap<Card,GTNode> children;
	private static TrickComp cmp = new TrickComp();
	
	public GTNode(GTNode p, Card pCard, Hand play, Hand o) {
		parent = p;
		player = play;
		oppon = o;
		parentCard = pCard;
		if (parent != null) {
			branchScore = parent.getBranchScore();
			depth = parent.getDepth() + 1;
		} else {
			branchScore = 0;
			depth = 0;
		}
		children = new HashMap<Card,GTNode>();
	}
	public int getDepth() {
		return depth;
	}
	public GTNode getChild(Card c) {
		return children.get(c);
	}
	public Card getPCard() {
		return parentCard;
	}
	public GTNode getParent() {
		return parent;
	}
	public void playerTurn(boolean pt) {
		pTurn = pt;
	}
	public boolean getTurn() {
		return pTurn;
	}
	public void trickComplete(boolean tc) {
		complete = tc;
	}
	public Iterable<GTNode> getChildren() {
		return children.values();
	}
	public void clear() {
		children = null;
	}
	public int getBranchScore() {
		return branchScore;
	}
	public void incBranchScore() {
		branchScore++;
	}
	
	public HashMap<Card,GTNode> findChildren() {
		if (!children.isEmpty()) { return children; }
		Hand scanHand;
		if (pTurn) {
			scanHand = player;
		} else {
			scanHand = oppon;
		}
		if (scanHand.size() == 0) {
			return null;
		}
		TreeSet<Card> scan;
		if (!complete) {
			scan = scanHand.getSuitList(parentCard.getSuit());
			if (scan.isEmpty()) {
				scan = scanHand.getHand();
			}
		} else {
			scan = scanHand.getHand();
		}
 		for (Card c: scan) {
			GTNode ans = parent;
			boolean valid = true;
			while (ans != null) {
				Card pCard = ans.getPCard();
				if (c.equals(pCard)) {
					valid = false;
					break;
				}
				ans = ans.getParent();
			}
			if (!valid) continue;
			GTNode node = new GTNode(this, c, player, oppon);
			if (complete) {
				node.trickComplete(false);
				node.playerTurn(!getTurn());
			} else {
				node.trickComplete(true);
				if ((!pTurn && cmp.compare(parentCard, c) > 0) || (pTurn && cmp.compare(parentCard, c) < 0)) { //If player wins trick
					ans = node;
					while (ans != null) {
						ans.incBranchScore();
						ans = ans.getParent();
					}
					node.playerTurn(true);
				} else {
					node.playerTurn(false);
				}
			}
			children.put(c, node);
		}
		return children;
	}
	public String toString() {
		return parentCard.toString();
	}
}
