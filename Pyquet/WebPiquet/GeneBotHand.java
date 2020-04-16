import java.util.Random;
import java.util.TreeSet;

//Discard: Minimum Card unless needed for straight or tuple
//Lead: Maximum card if has at least two winning cards in suit, else minimum card
//Follow: Minimum Card that beats lead if possible, else minimum
public class GeneBotHand extends Hand {
	protected static Random rng = new Random();
	protected double[][][] gene;

	public GeneBotHand(String n) {
		super(n);
	}

    public void setGene(double[][][] g) {
        gene = g;
    }

	public Card askDiscard() {
		int size = hand.size();
        double[] prob = new double[size];
        Card[] harray = new Card[hand.size()];
        harray = hand.toArray(harray);
        for (int i = 0; i < size; i++) {
            for (int j = 0; j < size; j++) {
                prob[i] += gene[harray[i].getRank()-7][harray[j].getRank()-7][0];
            }
        }
        for (int i = 1; i < size; i++) {
            prob[i] += prob[i-1];
        }
        double rand = prob[size-1]*rng.nextDouble();
        for (int i = 1; i < size; i++) {
            if (prob[i] > rand) {
                return harray[i-1];
            }
        }
        return harray[size-1];
	}
	public Card askLead() {
		int size = hand.size();
        double[] prob = new double[size];
        Card[] harray = new Card[hand.size()];
        harray = hand.toArray(harray);
        for (int i = 0; i < size; i++) {
            for (int j = 0; j < size; j++) {
                prob[i] += gene[harray[i].getRank()-7][harray[j].getRank()-7][1];
            }
        }
        for (int i = 1; i < size; i++) {
            prob[i] += prob[i-1];
        }
        double rand = prob[size-1]*rng.nextDouble();
        for (int i = 1; i < size; i++) {
            if (prob[i] > rand) {
                return harray[i-1];
            }
        }
        return harray[size-1];
	}
	public Card askFollow(Card lead) {
        TreeSet<Card> choices = getSuitList(lead.getSuit());
		if (choices.isEmpty()) {
			choices = hand;
		}
        int size = choices.size();
        double[] prob = new double[size];
        Card[] harray = new Card[size];
        harray = choices.toArray(harray);
        for (int i = 0; i < size; i++) {
            prob[i] = gene[harray[i].getRank()-7][lead.getRank()-7][2] + gene[harray[i].getRank()-7][harray[i].getRank()-7][2];
        }
        for (int i = 1; i < size; i++) {
            prob[i] += prob[i-1];
        }
        double rand = prob[size-1]*rng.nextDouble();
        for (int i = 1; i < size; i++) {
            if (prob[i] > rand) {
                return harray[i-1];
            }
        }
        return harray[size-1];
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