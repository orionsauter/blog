
import java.util.LinkedList;
import java.util.Random;

/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

/**
 *
 * @author orion
 */
public class Genetic {
    protected static Random rng = new Random();

    private static int fitness(double[][][] gene) {
        GeneBotHand player1 = new GeneBotHand("GeneBot");
        player1.setGene(gene);
        RandBotHand player2 = new RandBotHand("RandBot");
        Piquet game = new Piquet(player1,player2);
        game.talon.reseed(3);
        int fit = 0;
		for (int i = 0; i < 100; i++) {
            //System.out.println("Starting game "+i);
			if (i % 2 == 0) {
				game.elder = game.player1;
				game.younger = game.player2;
			} else {
				game.elder = game.player2;
				game.younger = game.player1;
			}
			int score = game.play();
			fit += score;
		}
        return fit;
    }

    private static int drawSample(int[] prob) {
        //int min = Integer.MAX_VALUE;
        //for (int i = 0; i < prob.length; i++) {
            //if (prob[i] < min) {
            //    min = prob[i];
            //}
        //}
        int[] cumprob = new int[prob.length];
        for (int i = 0; i < prob.length; i++) {
            //prob[i] -= min;
            if (prob[i] < 0) {
                prob[i] = 0;
            }
            cumprob[i] = prob[i];
            if (i > 0) {
                cumprob[i] += cumprob[i-1];
            }
        }
        double rand = rng.nextDouble();
        for (int i = 0; i < prob.length; i++) {
            if (cumprob[i]/cumprob[cumprob.length-1] > rand) {return i;}
        }
        return cumprob.length-1;
    }

    private static void stats(int[] fit) {
        double mean = 0;
        int max = Integer.MIN_VALUE;
        int min = Integer.MAX_VALUE;
        for (int i = 0; i < fit.length; i++) {
            mean += fit[i];
            if (fit[i] > max) {
                max = fit[i];
            }
            if (fit[i] < min) {
                min = fit[i];
            }
        }
        mean /= fit.length;
        System.out.println(min+","+mean+","+max);
    }

    public static void main(String args[]) {
        int popsize = 100;
        LinkedList<double[][][]> pop = new LinkedList<double[][][]>();
        int[] fit = new int[popsize];
        for (int i = 0; i < popsize; i++) {
            double[][][] gene = new double[8][8][3];
            for (int r = 0; r < 8; r++) {
                for (int c = 0; c < 8; c++) {
                    for (int p = 0; p < 3; p++) {
                        gene[r][c][p] = rng.nextDouble();
                    }
                }
            }
            pop.add(gene);
            fit[i] = fitness(gene);
        }
        stats(fit);

        for (int gen = 0; gen < 100; gen++) {
            LinkedList<double[][][]> newpop = new LinkedList<double[][][]>();
            int[] newfit = new int[popsize];
            for (int i = 0; i < popsize; i += 2) {
                int motheri = drawSample(fit);
                int temp = fit[motheri];
                fit[motheri] = 0;
                int fatheri = drawSample(fit);
                fit[motheri] = temp;
                double[][][] mother = pop.get(motheri);
                double[][][] father = pop.get(fatheri);

                double[][][] child1 = new double[8][8][3];
                double[][][] child2 = new double[8][8][3];
                int cutoff = rng.nextInt(192);
                for (int r = 0; r < 8; r++) {
                    for (int c = 0; c < 8; c++) {
                        for (int p = 0; p < 3; p++) {
                            double mutate = 0;
                            if (rng.nextDouble() < .01) {
                                mutate = rng.nextDouble() - .5;
                            }
                            if (r*24+c*3+p < cutoff) {
                                child1[r][c][p] = mother[r][c][p] + mutate;
                                child2[r][c][p] = father[r][c][p] + mutate;
                            } else {
                                child2[r][c][p] = mother[r][c][p] + mutate;
                                child1[r][c][p] = father[r][c][p] + mutate;
                            }
                        }
                    }
                }
                if (rng.nextDouble() < .6) {
                    newpop.add(child1);
                    newpop.add(child2);
                    newfit[i] = fitness(child1);
                    newfit[i+1] = fitness(child2);
                } else {
                    newpop.add(mother);
                    newpop.add(father);
                    newfit[i] = fit[motheri];
                    newfit[i+1] = fit[fatheri];
                }
            }
            pop = newpop;
            fit = newfit;
            stats(fit);
        }

    }
}
