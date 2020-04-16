import java.util.LinkedList;
import java.util.TreeSet;


public class GameTree {
	private GTNode pos;
	private Hand player;
	private Hand oppon;
	private int curDepth;
	
	public GameTree(Hand p, Hand o, Card lead) {
		player = p;
		oppon = o;
		pos = new GTNode(null, lead, player, oppon);
		pos.playerTurn(true);
		pos.trickComplete(lead == null);
		curDepth = 7;
	}
	public GTNode getPos() {
		return pos;
	}
	public GTNode setPos(Card c) {
		pos = pos.getChild(c);
		if (pos == null) { return pos; }
		curDepth++;
		GTNode ans = pos.getParent();
		while (ans != null) {
			ans.clear();
			ans = ans.getParent();
		}
		buildTree();
		return pos;
	}
	public Card findBest(TreeSet<Card> choices) {
		int max = -1;
		Card maxCard = null;
		for (Card c: choices) {
			if (pos.getChild(c) == null) { continue; }
			int test = pos.getChild(c).getBranchScore();
			if (test > max) {
				max = test;
				maxCard = c;
			}
		}
		return maxCard;
	}
	public void buildTree() {
		if (player.size() < 2) { return; }
		LinkedList<GTNode> search = new LinkedList<GTNode>();
		search.addLast(pos);
		while (!search.isEmpty()) {
			GTNode node = search.removeFirst();
			search.addAll(node.findChildren().values());
			if (node.getDepth() > curDepth) break;
		}
	}
	
	public static void main(String[] args) {
		Deck d = new Deck("Talon");
		d.buildDeck(7, 14);
		d.shuffle();
		Hand player1 = new Hand("P1");
		Hand player2 = new Hand("P2");
		for (int i = 0; i < 12; i++) {
			player1.addCard(d.takeTop());
			player2.addCard(d.takeTop());
		}
		GameTree tree = new GameTree(player1, player2, null);
		System.out.println(player1);
		System.out.println(player2);
		tree.buildTree();
	}
}
