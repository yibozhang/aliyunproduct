package com.alibaba.edas.carshop.OSS;

import java.io.ByteArrayInputStream;

import com.aliyun.oss.OSSClient;
import com.aliyun.oss.common.utils.BinaryUtil;
import com.aliyun.oss.model.Callback;
import com.aliyun.oss.model.ObjectMetadata;
import com.aliyun.oss.model.PutObjectRequest;
import com.aliyun.oss.model.PutObjectResult;

public class UserDemo implements Runnable {

	   
	   
	public static void main(String args[]) {
	      RunnableDemo R1 = new RunnableDemo( "Thread-1");
	      R1.start();
	      
	      /*RunnableDemo R2 = new RunnableDemo( "Thread-2");
	      R2.start();
	      
	      RunnableDemo R3 = new RunnableDemo( "Thread-3");
	      R3.start();
	      
	      RunnableDemo R4 = new RunnableDemo( "Thread-4");
	      R4.start();
	      
	      RunnableDemo R5 = new RunnableDemo( "Thread-5");
	      R5.start();*/
	   }
	public void run() {
		// TODO Auto-generated method stub
		
	}   
}


class RunnableDemo implements Runnable {
	
	private static String accessKeyId = "LTAIVuMxeNAGmBQa";
	private static String accessKeySecret = "YuTMo5W4Z5tf4pzyIVtjrt90CNJtJV";
	private static String endpoint = "http://oss-cn-beijing.aliyuncs.com/";
	
	OSSClient ossclient = new OSSClient(endpoint, accessKeyId,accessKeySecret);
	
	   private Thread t;
	   private String threadName;
	   
	   RunnableDemo( String name) {
	      threadName = name;
	      System.out.println("Creating " +  threadName );
	   }
	   
	   public void run() {
	      System.out.println("Running " +  threadName );
	      
	         for(int i = 0; i < 10000; i++) {
	        	 try {
	            System.out.println("Thread: " + threadName + ", " + i);
	            
	            //上传部分
	            String content = new String();
	    		content="12345";
	    		// 创建上传Object的Metadata
	    		ObjectMetadata meta = new ObjectMetadata();
	    		// 设置上传文件长度
	    		meta.setContentLength(content.length());
	    		// 设置上传MD5校验
	    		String md5 = BinaryUtil.toBase64String(BinaryUtil.calculateMd5(content.getBytes()));
	    		meta.setContentMD5(md5);
	    		// 设置上传内容类型
	    		meta.setContentType("text/plain");
	    		meta.setServerSideEncryption("AES256");
	    		// 上传文件
	    		
	    		PutObjectRequest putObjectRequest=new PutObjectRequest("ruide", "1.txt", new ByteArrayInputStream(content.getBytes()), meta);
	    		Callback callback = new Callback();
	    		callback.setCallbackUrl("http://47.93.116.168/Revice.ashx");
	    		callback.setCallbackBody("bucket:${bucket},size:${size}");
	    		putObjectRequest.setCallback(callback);
	    		
	    		PutObjectResult por = ossclient.putObject(putObjectRequest);
	    		
	    		System.out.println("requestid:"+por.getRequestId());
	    		por.getCallbackResponseBody().close();
	            //
	            // 让线程睡眠一会
	            Thread.sleep(0);
	        	 }catch (Exception e) {
	    	         System.out.println("Thread " +  threadName + " interrupted.");
	    	      }
	         }
	      
	      System.out.println("Thread " +  threadName + " exiting.");
	   }
	   
	   public void start () {
		
	      System.out.println("Starting " +  threadName );
	      if (t == null) {
	         t = new Thread (this, threadName);
	         t.start ();
	     
		   }
	   }
}
	