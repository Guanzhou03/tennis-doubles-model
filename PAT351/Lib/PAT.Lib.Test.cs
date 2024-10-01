using System;
using System.Collections.Generic;
using System.Text;
using PAT.Common.Classes.Expressions.ExpressionClass;
//the namespace must be PAT.Lib, the class and method names can be arbitrary
namespace PAT.Lib
{
	public class Node  : ExpressionValue {
		private int data = -1;
		public Node() {}
		public void SetData(int input) {
			data = input;
			System.IO.File.WriteAllText(@"C:\temp\pat_store.txt", data.ToString());
			Singleton s = Singleton.Instance;
			s.SetData(input);
		}
		public int GetData() {
//		    data = Int32.Parse(System.IO.File.ReadAllText(@"C:\temp\pat_store.txt"));
			Singleton s = Singleton.Instance;
//			return s.GetData();
			return data;
		}
		/// Return the string representation of the hash table.
        /// This method must be overriden
        public override string ToString() {
            return "[" + data + "]";
        }
        /// Return a deep clone of the hash table
        /// NOTE: this must be a deep clone, shallow clone may lead to strange behaviors.
        /// This method must be overriden
        public override ExpressionValue GetClone() {
//            return new Node();
			Node x = new Node();
			x.SetData(data);
			return x;
        }
        
        public override string ExpressionID {
        	get {
        		return "1";
        	}
        }
    }
    
    public sealed class Singleton {
    	private static Singleton instance = null;
    	private static readonly object padlock = new object();
    	private int data = -1;
    	
    	Singleton() {
	    }
	    
	    public static Singleton Instance {
	    	get {
	    		lock (padlock) {
	    			if (instance == null) {
	    				instance = new Singleton();
	    			}
	    			return instance;
	    		}
	    	}
	    }
	    
	    public void SetData(int input) {
	    	data = input;
	    }
	    
	    public int GetData() {
	    	return data;
	    }
    }
}
