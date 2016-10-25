package problem2;

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

public class Stemming {

	public static HashMap<String, Integer> stemMap;
	public static Integer totalStems;
	Stemmer s;

	public Stemming() {
		s = new Stemmer();
		totalStems=0;
		stemMap = new HashMap<String, Integer>();
	}

	public void process(HashMap<String, Integer> tokenMap) {
		//reference for the below code: Stemmer.java main function
		for (String key : tokenMap.keySet()) {
			s.add(key.toCharArray(),key.length());
			s.stem();
			String temp = s.toString();
			if (stemMap.containsKey(temp)) {
				stemMap.put(temp, stemMap.get(temp)+1);
			} else {
				stemMap.put(temp, 1);
			}
		}
		stemMap=(HashMap<String, Integer>) sortByValue(stemMap);
	}
	
	public int distinctTotalStemsPerDocument(ArrayList<Set<String>> A){
		Integer count=0;
		
		for(Set<String> set:A){
			Set s2=new HashSet<String>();
			for(String temp:set){
				s.add(temp.toCharArray(),temp.length());
				s.stem();
				s2.add(s.toString());
			}
			count+=s2.size();
		}
		
		return count;
	}
	
	
	//function to sort the map according to it's value in decreasing order
	private static <K, V> Map<K, V> sortByValue(Map<K, V> map) {
	    List<Entry<K, V>> list = new LinkedList<Entry<K, V>>(map.entrySet());
	    Collections.sort(list, new Comparator<Object>() {
	        @SuppressWarnings("unchecked")
	        public int compare(Object o1, Object o2) {
	            return ((Comparable<V>) ((Map.Entry<K, V>) (o1)).getValue()).compareTo(((Map.Entry<K, V>) (o2)).getValue())*-1;
	        }
	    });

	    Map<K, V> result = new LinkedHashMap<K, V>();
	    for (Iterator<Entry<K, V>> it = list.iterator(); it.hasNext();) {
	        Map.Entry<K, V> entry = (Map.Entry<K, V>) it.next();
	        result.put(entry.getKey(), entry.getValue());
	    }

	    return result;
	}
	
	public Integer numberOfTokensOccurOnce(){
		
		Integer count=0;
		for(Integer val:stemMap.values()){
			if(val==1){
				count+=1;
			}
		}
		return count;
	}
	public static void main(String [] args){
			
		Stemming s=new Stemming();
		HashMap<String, Integer> h=new HashMap<String, Integer>();
		h.put("the", 1);
		s.process(h);
		System.out.println(s.stemMap);
		
		
	}
	
}
