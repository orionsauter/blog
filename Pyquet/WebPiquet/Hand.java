import java.util.ArrayList;
import java.util.Iterator;
import java.util.Scanner;
import java.util.TreeSet;

public class Hand implements Iterable<Card> {
	protected static SortComp cmp = new SortComp();
	private static final Card DUMMY = new Card(0,0);
	protected TreeSet<Card> hand;
	protected String name;
	protected int score;
	protected int tricks;
	protected Scanner scan;
	protected TreeSet<Card> unseen;
	protected Hand opponent;
	
	public Hand(String n) {
		hand = new TreeSet<Card>(cmp);
		unseen = new TreeSet<Card>(cmp);
		name = n;
		score = 0;
		tricks = 0;
		scan = new Scanner(System.in);
	}
	
	public Hand clone() {
		Hand cln = new Hand(name+" Clone");
		cln.addAll(getHand());
		cln.unseen = (TreeSet<Card>) unseen.clone();
		cln.setOpponent(getOpponent());
		cln.addScore(getScore());
		for (int i = 0; i < getTricks(); i++) {
			cln.incTricks();
		}
		return cln;
	}
// Basic Operations
	public boolean addCard(Card c) {
		markSeen(c);
		return hand.add(c);
	}
	public boolean addAll(TreeSet<Card> c) {
		markSeen(c);
		return hand.addAll(c);
	}
	public boolean removeCard(Card c) {
		return hand.remove(c);
	}
	public Card getIndex(int index) {
		int i = 0;
		for (Card c : hand) {
			if (i == index) {
				return c;
			}
			i++;
		}
		return null;
	}
	public Card removeIndex(int index) {
		Card c = getIndex(index);
		removeCard(c);
		return c;
	}
	public Iterator<Card> iterator() {
		return hand.iterator();
	}
	public ArrayList<Card> toArrayList() {
		ArrayList<Card> al = new ArrayList<Card>();
		for (Card c : hand) {
			al.add(c);
		}
		return al;
	}
	public void clear() {
		tricks = 0;
		hand.clear();
	}
	public boolean isHuman() {
		return true;
	}
	public TreeSet<Card> getSuitList(int suit) {
		TreeSet<Card> out = new TreeSet<Card>(cmp);
		for (Card c : hand) {
			if (c.getSuit() == suit) out.add(c);
		}
		return out;
	}
	public TreeSet<Card> getUnseenSuit(int suit) {
		TreeSet<Card> out = new TreeSet<Card>(cmp);
		for (Card c : unseen) {
			if (c.getSuit() == suit) out.add(c);
		}
		return out;
	}
	public TreeSet<Card> getUnseen() {
		return unseen;
	}
	public void markSeen(Card c) {
		unseen.remove(c);
	}
	public void markSeen(TreeSet<Card> c) {
		unseen.removeAll(c);
	}
	public void initUnseen(Deck d) {
		unseen.clear();
		for (Card c : d.getPile()) {
			unseen.add(c);
		}
	}
	public void setOpponent(Hand h) {
		opponent = h;
	}
	public Hand getOpponent() {
		return opponent;
	}
	public TreeSet<Card> getHand() {
		return hand;
	}
	public void setVars(int r1, int h1, int m1, int d1) {
		// Dummy Method for KevinBot
	}
	
// Scoring
	public int point() {
		if (hand.size() == 0) return 0;
		int[] suits = new int[4];
		for (Card c : hand) {
			suits[c.getSuit()] += 1;
		}
		return arrayMax(suits);
	}
	public int scorePoint() {
		score += point();
		return getScore();
	}
	public int[] tuples() {
		int[] tups = new int[8];
		if (hand.size() == 0) return tups;
		for (Card c : hand) {
			tups[c.getRank() - 7] += 1;
		}
		return tups;
	}
	public int scoreTuples() {
		int[] tups = tuples();
		for (int i = 0; i < 8; i++) {
			int val = tups[i];
			if (val > 3) {
				score += 14;
			} else if (val > 2) {
				score += 3;
			}
		}
		return getScore();
	}
	public String tupleLookup(int tuple) {
		if (tuple == 48) {
			return "Triplet of 7s";
		} else if (tuple == 51) {
			return "Triplet of 8s";
		} else if (tuple == 54) {
			return "Triplet of 9s";
		} else if (tuple == 57) {
			return "Triplet of 10s";
		} else if (tuple == 60) {
			return "Triplet of Js";
		} else if (tuple == 63) {
			return "Triplet of Qs";
		} else if (tuple == 66) {
			return "Triplet of Ks";
		} else if (tuple == 69) {
			return "Triplet of As";
		} else if (tuple == 92) {
			return "Quadruplet of 7s";
		} else if (tuple == 96) {
			return "Quadruplet of 8s";
		} else if (tuple == 100) {
			return "Quadruplet of 9s";
		} else if (tuple == 104) {
			return "Quadruplet of 10s";
		} else if (tuple == 108) {
			return "Quadruplet of Js";
		} else if (tuple == 112) {
			return "Quadruplet of Qs";
		} else if (tuple == 116) {
			return "Quadruplet of Ks";
		} else if (tuple == 120) {
			return "Quadruplet of As";
		} else {
			return "No valid tuples";
		}
	}
	/* Tuple return values:
	 * 1	2	3	4
	 * 7	22	48	92
	 * 8	24	51	96
	 * 9	26	54	100
	 * 10	28	57	104
	 * 11	30	60	108
	 * 12	32	63	112
	 * 13	34	66	116
	 * 14	36	69	120
	 */
	public int maxTuple() {
		int[] tups = tuples();
		for (int i = 0; i < 8; i++) {
			int temp = tups[i];
			tups[i] = ((i + 7) + (temp * temp)) * temp;
		}
		return arrayMax(tups);
	}
	public String straightLookup(int str) {
		if (str < 54) {
			return "No valid runs";
		} else if (str < 104) {
			return "Run of 3";
		} else if (str < 180) {
			return "Run of 4";
		} else if (str < 288) {
			return "Run of 5";
		} else if (str < 434) {
			return "Run of 6";
		} else if (str < 624) {
			return "Run of 7";
		} else {
			return "Run of 8";
		}
	}
	/* Straight return values:
	 * 1	2	3	4	5	6	7	8
	 * 7	X	X	X	X	X	X	X
	 * 8	24	X	X	X	X	X	X
	 * 9	26	54	X	X	X	X	X
	 * 10	28	57	104	X	X	X	X
	 * 11	30	60	108	180	X	X	X
	 * 12	32	63	112	185	288	X	X
	 * 13	34	66	116	190	294	434	X
	 * 14	36	69	120	195	300	441	624
	 */
	public int straight() {
		if (hand.size() == 0) return 0;
		Card high = DUMMY;
		int maxStr = 0;
		for (int suit = 0; suit < 4; suit++) {
			Card last = DUMMY;
			int str = 1;
			for (Card curCard: getSuitList(suit)) {
				if (last.getRank() == 0) {
					last = curCard;
					continue;
				}
				if (curCard.getRank() == last.getRank() + 1) {
					str++;
				} else {
					str = 1; // Reset straight length
				}
				if (((curCard.getRank() + (str * str)) * str) > ((high.getRank() + (maxStr * maxStr)) * maxStr)) { // If we found a new max
					maxStr = str;
					high = curCard; // Keep track of high card
				}
				last = curCard;
			}
		}
		return (high.getRank() + (maxStr * maxStr)) * maxStr;
	}
	public int scoreStraight() {
		int str = straight();
		if (str > 600) {
			score += 18;
		} else if (str > 400) {
			score += 17;
		} else if (str > 200) {
			score += 16;
		} else if (str > 150) {
			score += 15;
		} else if (str > 100) {
			score += 14;
		} else if (str > 50) {
			score += 3;
		}
		return getScore();
	}
	
// Info Methods
	public String toString() {
		//String out = name + ": ";
		String out = hand.toString();
		return out;
	}
	public String getName() { return name; }
	
	public int getScore() { return score; }
	public int addScore(int i) {
		score += i;
		return getScore();
	}
	public void clearScore() { score = 0; }
	
	public boolean hasSuit(int s) {
		for (Card c : hand) {
			if (c.getSuit() == s) return true;
		}
		return false;
	}
	
	public void incTricks() { tricks++; }
	public int getTricks() { return tricks; }
	public Card askCard() {
		int input = scan.nextInt();
		return getIndex(input);
	}
	public Card askDiscard() {
		return askCard();
	}
	public Card askLead() {
		return askCard();
	}
	public Card askFollow(Card lead) {
		return askCard();
	}
	public int size() { return hand.size(); }
// Auxiliary Methods
	protected int arrayMax(int[] array) {
		int max = 0;
		for (int i : array) {
			if (i > max) {
				max = i;
			}
		}
		return max;
	}
}
