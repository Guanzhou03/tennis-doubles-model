using System;
using System.Collections.Generic;
using System.Text;
//the namespace must be PAT.Lib, the class and method names can be arbitrary
namespace PAT.Lib
{
    /// <summary>
    /// The math library that can be used in your model.
    /// all methods should be declared as public static.
    /// 
    /// The parameters must be of type "int", or "int array"
    /// The number of parameters can be 0 or many
    /// 
    /// The return type can be bool, int or int[] only.
    /// 
    /// The method name will be used directly in your model.
    /// e.g. call(max, 10, 2), call(dominate, 3, 2), call(amax, [1,3,5]),
    /// 
    /// Note: method names are case sensetive
    /// </summary>
    public class SoccerLib
    {
    	private static Random rnd = new Random();
    	
	       public static bool dummy(int[] values)
        {
		        return true;
        }
        
        public static int[] shoot(int p_i, int ball, int[] t1_r, int[] t1_c, int[] t2_r, int[] t2_c, int PREC)
        {
        	double precision = PREC/100.0;
        	int num_t2_players = 0;
        	for (int i=0; i<t2_r.Length; i++){
        		if (t2_c[i]*3+t2_r[i] == ball){
        			num_t2_players = num_t2_players + 1;
        		}
        	}
        	double by_t2 = 1-Math.Pow(0.5, num_t2_players);
        	double distance = Math.Sqrt((ball/3-4)*(ball/3-4) + (ball%3-1)*(ball%3-1));
        	double success_rate = Math.Pow(precision, distance);
        	double missed = by_t2 + (1-by_t2)*(1-success_rate);
        	
        	int[] result = new int[2];
        	
        	double rnd_num = rnd.NextDouble();
        	double rnd_num2 = rnd.NextDouble();
        	if (rnd_num < by_t2) {
        		result[0] = 1;
        		result[1] = 0;
        	} else if (rnd_num < missed) {
        		result[0] = 0;
        		if (rnd_num2 < 0.25) {
        			result[1] = 7;
        		} else if (rnd_num2 < 0.5) {
        			result[1] = 9;
        		} else if (rnd_num2 < 0.75) {
        			result[1] = 10;
        		} else {
        			result[1] = 11;
        		}
        	} else {
        		result[0] = 2;
        		result[1] = 0;
        	}
        	
        	String data = "shoot:";
        	data = data + by_t2.ToString() + "," + missed.ToString() + "," + rnd_num.ToString() + "," + rnd_num2.ToString() + "," + result[0].ToString() + "," + result[1].ToString();
        	System.IO.File.AppendAllText(@"C:\temp\pat_store.txt", data.ToString()+"\n");
        	
        	return result;
        }
        
        public static int[] dribble(int p_i, int ball, int[] t1_r, int[] t1_c, int[] t2_r, int[] t2_c, int PREC, int direction)
        {
        	double precision = PREC/100.0;
        	int num_t2_players = 0;
        	for (int i=0; i<t2_r.Length; i++){
        		if (t2_c[i]*3+t2_r[i] == ball){
        			num_t2_players = num_t2_players + 1;
        		}
        	}
        	double by_t2 = 1-Math.Pow(0.5, num_t2_players);
        	double distance = 0.5;
        	double success_rate = Math.Pow(precision, distance);
        	double missed = by_t2 + (1-by_t2)*(1-success_rate);
        	
        	int[] result = new int[2];
        	
        	double rnd_num = rnd.NextDouble();
        	double rnd_num2 = rnd.NextDouble();
        	if (rnd_num < by_t2) {
        		result[0] = 1;
        		result[1] = 0;
        	} else if (rnd_num < missed) {
        		result[0] = 0;
        		result[1] = ball;
        	} else {
        		result[0] = 0;
        		if (direction == 0) {
        			result[1] = ball-1;
        		} else if (direction == 1) {
        			result[1] = ball+1;
        		} else if (direction == 2) {
        			result[1] = ball-3;
        		} else {
        			result[1] = ball+3;
        		}
        	}
        	
        	String data = "dribble:";
        	data = data + by_t2.ToString() + "," + missed.ToString() + "," + rnd_num.ToString() + "," + rnd_num2.ToString() + "," + result[0].ToString() + "," + result[1].ToString();
        	System.IO.File.AppendAllText(@"C:\temp\pat_store.txt", data.ToString()+"\n");
        	
        	return result;
        }
        
        public static int[] passing(int p_i, int p_j, int[] t1_r, int[] t1_c, int[] t2_r, int[] t2_c, int PREC)
        {
        	double precision = PREC/100.0;
        	int num_t2_players = 0;
        	for (int i=0; i<t2_r.Length; i++){
        		if (t2_c[i]*3+t2_r[i] == t2_c[p_i]*3+t2_r[p_i]){
        			num_t2_players = num_t2_players + 1;
        		}
        		if (t2_c[i]*3+t2_r[i] == t2_c[p_j]*3+t2_r[p_j]){
        			num_t2_players = num_t2_players + 1;
        		}
        	}
        	double by_t2 = 1-Math.Pow(0.5, num_t2_players);
        	double distance = Math.Sqrt((t1_r[p_i]-t1_r[p_j])*(t1_r[p_i]-t1_r[p_j]) + (t1_c[p_i]-t1_c[p_j])*(t1_c[p_i]-t1_c[p_j]));
        	double success_rate = Math.Pow(precision, distance);
        	double missed = by_t2 + (1-by_t2)*(1-success_rate);
        	
        	int[] result = new int[2];
        	
        	double rnd_num = rnd.NextDouble();
        	double rnd_num2 = rnd.NextDouble();
        	if (rnd_num < by_t2) {
        		result[0] = 1;
        		result[1] = 0;
        	} else if (rnd_num < missed) {
        		result[0] = 0;
        		if (rnd_num2 < 0.25) {
        			if (t1_r[p_j]>0) {
        				result[1] = t1_c[p_j]*3+t1_r[p_j]-1;
        			} else {
        				result[0] = 1;
        				result[1] = 0;
        			}
        		} else if (rnd_num2 < 0.5) {
        			if (t1_r[p_j]<2) {
        				result[1] = t1_c[p_j]*3+t1_r[p_j]+1;
        			} else {
        				result[0] = 1;
        				result[1] = 0;
        			}
        		} else if (rnd_num2 < 0.75) {
        			if (t1_c[p_j]>0) {
        				result[1] = t1_c[p_j]*3+t1_r[p_j]-3;
        			} else {
        				result[0] = 1;
        				result[1] = 0;
        			}
        		} else {
        			if (t1_c[p_j]<3) {
        				result[1] = t1_c[p_j]*3+t1_r[p_j]+3;
        			} else {
        				result[0] = 1;
        				result[1] = 0;
        			}
        		}
        	} else {
        		result[0] = 0;
        		result[1] = t1_c[p_j]*3+t1_r[p_j];
        	}
        	
        	String data = "pass:";
        	data = data + by_t2.ToString() + "," + missed.ToString() + "," + rnd_num.ToString() + "," + rnd_num2.ToString() + "," + result[0].ToString() + "," + result[1].ToString();
        	System.IO.File.AppendAllText(@"C:\temp\pat_store.txt", data.ToString()+"\n");
        	
        	return result;
        }
    }
}
