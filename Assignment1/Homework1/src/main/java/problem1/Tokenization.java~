package problem1;

import java.io.File;
import java.io.IOException;

import problem2.Stemming;

public class Tokenization {

	public static void main(String args[]) throws IOException {
		File folder = new File(args[0]);
		Parser parser = new Parser();
		parser.ParseFolder(folder);
		Stemming s = new Stemming();
		Integer sum = getTotalTokens(parser);

		System.out.println("Part 1");

		System.out.print("Total Number of tokens(including duplicates): ");
		System.out.println(sum);

		System.out.print("Number of unique tokens: ");
		System.out.println(parser.tokenMap.size());
		
		System.out.print("Average number of (including duplicates)token per document: ");
		System.out.println((double)(sum / parser.documents));

		System.out.print("Average number of (distinct)token per document: ");
		System.out.println((double)(parser.tokenMap.size() / parser.documents));

		System.out.print("Number of tokens that occur only once: ");
		System.out.println(getTokenOccurOnce(parser));

		System.out.println("30 Most frequent tokens: ");
		getTokenOccurMost(parser);

		System.out.println("\n\n");
		System.out.println("Part 2");
		s.process(parser.tokenMap);

		System.out.print("Number of distinct stems: ");
		System.out.println(s.stemMap.size());

		System.out.print("Number of stems that occur only once: ");
		System.out.println(s.numberOfTokensOccurOnce());

		System.out.println("30 most frequent stems");
		mostFrequentStems(s);
		
//		System.out.print("Average number of (distinct)stems per document: ");
//		System.out.println((double)(s.stemMap.size()/parser.documents));
		
		System.out.print("Average number of (distinct)stems per document: ");
		System.out.println((double)(s.distinctTotalStemsPerDocument(parser.distinctTokenDocument)/parser.documents));
	}

	private static Integer getTotalTokens(Parser parser) {
		Integer sum = 0;
		for (Integer temp : parser.tokenMap.values()) {
			sum += temp;
		}
		return sum;
	}

	private static Integer getTokenOccurOnce(Parser parser) {
		Integer res = 0;
		for (Integer temp : parser.tokenMap.values()) {
			if (temp == 1) {
				res += 1;
			}
		}
		return res;
	}

	private static void getTokenOccurMost(Parser parser) {
		Integer count = 0;
		for (String temp : parser.tokenMap.keySet()) {
			count += 1;
			System.out.println(count+". "+temp + " " + parser.tokenMap.get(temp));
			if (count >= 30) {
				break;
			}
		}
	}

	private static void mostFrequentStems(Stemming s) {
		Integer count = 0;
		for (String temp : s.stemMap.keySet()) {
			count += 1;
			System.out.println(count+". "+temp + " " + s.stemMap.get(temp));
			if (count >= 30) {
				break;
			}
		}

	}

}
