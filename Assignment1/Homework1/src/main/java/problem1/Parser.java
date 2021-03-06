package problem1;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.LinkedHashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Set;

public class Parser {
	public static HashMap<String, Integer> tokenMap;
	public static ArrayList<Set<String>> distinctTokenDocument;
	public static Integer documents;

	Parser() {
		tokenMap = new HashMap<String, Integer>();
		distinctTokenDocument= new ArrayList<Set<String>>();
		documents = 0;
	}

	//reference for the method:http://stackoverflow.com/questions/1844688/read-all-files-in-a-folder
	// parse the folder
	void ParseFolder(File folder) throws IOException {
		for (File fileEntry : folder.listFiles()) {
			if (fileEntry.isDirectory()) {
				ParseFolder(fileEntry);
			} else {
				ParseFile(fileEntry);
				documents += 1;
			}
		}
	}

	// parse the file
	void ParseFile(File fileEntry) throws IOException {
		BufferedReader br = new BufferedReader(new FileReader(fileEntry));
		Set temp= new HashSet<String>();
		String line;
		while ((line = br.readLine()) != null) {
			br.readLine();
			process(line,temp);
		}
		distinctTokenDocument.add(temp);
		tokenMap = (HashMap<String, Integer>) sortByValue(tokenMap);
	}

	void process(String line,Set<String> set) {

		// replace the SGML tags with space
		line = line.replaceAll("\\<.*?>", " ");

		// replace the digist with blank
		line = line.replaceAll("[\\d+]", "");

		// replace the special characters
		line = line.replaceAll("[+^:,?;=%#&~`$!@*_)/(}{\\.]", "");

		// remove the apostrophe s
		line = line.replaceAll("\\'s", "");

		// replace the apostrophe with space
		line = line.replaceAll("\\'", " ");

		// replace the dash with space
		line = line.replaceAll("-", " ");

		// replace multiple white spaces with a single space
		line = line.replaceAll("\\s+", " ");
		String[] tokens = line.split(" ");

		for (String temp : tokens) {
			if (tokenMap.containsKey(temp)) {
				tokenMap.put(temp, tokenMap.get(temp) + 1);
			} else {
				tokenMap.put(temp, 1);
			}
			set.add(temp);
		}

	}

	// function to sort the map according to it's value in decreasing order
	private static <K, V> Map<K, V> sortByValue(Map<K, V> map) {
		List<Entry<K, V>> list = new LinkedList<Entry<K, V>>(map.entrySet());
		Collections.sort(list, new Comparator<Object>() {
			@SuppressWarnings("unchecked")
			public int compare(Object o1, Object o2) {
				return ((Comparable<V>) ((Map.Entry<K, V>) (o1)).getValue())
						.compareTo(((Map.Entry<K, V>) (o2)).getValue()) * -1;
			}
		});

		Map<K, V> result = new LinkedHashMap<K, V>();
		for (Iterator<Entry<K, V>> it = list.iterator(); it.hasNext();) {
			Map.Entry<K, V> entry = (Map.Entry<K, V>) it.next();
			result.put(entry.getKey(), entry.getValue());
		}

		return result;
	}

}
