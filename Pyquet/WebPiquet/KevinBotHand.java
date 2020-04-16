import java.util.ArrayList;
import java.util.TreeSet;


public class KevinBotHand extends Hand {
	private static TrickComp cmp = new TrickComp();
	private int r, h, m, d;
	
	public KevinBotHand(String n) {
		super(n);
		r = 10;
		h = -205;
		m = 65;
		d = 70;
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
		float index = calcIndex();
		if (index < 0) {
			return minCard(getSuitList(dispSuit()));
		} else {
			return maxCard(getSuitList(dispSuit()));
		}
	}
	public Card askFollow(Card lead) {
		if (getSuitList(lead.getSuit()).isEmpty()) {
			return minCard(getSuitList(dispSuit()));
		} else {
			float index = calcIndex();
			if (index < 0) {
				return minCard(getSuitList(lead.getSuit()));
			} else {
				return maxCard(getSuitList(lead.getSuit()));
			}
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
	private int calcDisparity(int i) {
		if (getUnseenSuit(i).size() > getOpponent().point()) {
			return getSuitList(i).size() - getOpponent().point();
		} else {
			return getSuitList(i).size() - getUnseenSuit(i).size();
		}
	}
	private int dispSuit() {
		int maxD = Integer.MIN_VALUE;
		int maxS = -1;
		for (int i = 0; i < 4; i++) {
			if (getSuitList(i).isEmpty()) { continue; }
			int disp = calcDisparity(i);
			if (disp > maxD) {
				maxD = disp;
				maxS = i;
			}
		}
		return maxS;
	}
	public int calcSuitIndex(int i) {
		int runSize = 0;
		int holeSize = 0;
		int missedRun = 0;
		int disparity = 0;
		TreeSet<Card> suit = getSuitList(i);
		disparity += Math.abs(calcDisparity(i));
		ArrayList<Card> suitArray = new ArrayList<Card>();
		for (Card c: suit) {
			suitArray.add(0, c);
		}
		int curRank = 14;
		boolean hole = false;
		for (int j = 0; j < suitArray.size(); j++) {
			Card c = suitArray.get(j);
			if (curRank == c.getRank()) {
				if (hole) {
					missedRun++;
				} else {
					runSize++;
				}
			} else {
				j--; // Don't advance to next card yet
				if (getUnseen().contains(new Card(curRank, i))) {
					hole = true;
					holeSize++;
				} else {
					if (hole) {
						missedRun++;
					} else {
						runSize++;
					}
				}
			}
			curRank--;
		}
		return (r*runSize + h*holeSize + m*missedRun + d*disparity)/100;
	}
	public float calcIndex() {
		float index = 0;
		for (int i = 0; i < 4; i++) {
			index += calcSuitIndex(i);
		}
		return index;
	}
	public void setVars(int r1, int h1, int m1, int d1) {
		r = r1;
		h = h1;
		m = m1;
		d = d1;
	}
	public static void main(String[] args) {
		Deck talon = new Deck("Talon");
		talon.buildDeck(7, 14);
		talon.shuffle();
		KevinBotHand player1 = new KevinBotHand("KevinBot");
		KevinBotHand player2 = new KevinBotHand("KevinBot");
		player1.setOpponent(player2);
		player2.setOpponent(player1);
		for (int i = 0; i < 12; i++) {
			player1.addCard(talon.takeTop());
			player2.addCard(talon.takeTop());
		}
		player1.setVars(10, -10, 5, 10);
		System.out.println(player1);
		System.out.println(player1.calcIndex());
		player2.setVars(10, -10, 5, 10);
		System.out.println(player2);
		System.out.println(player2.calcIndex());
	}
}
