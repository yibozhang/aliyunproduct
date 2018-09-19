package com.alibaba.edas.carshop.OSS;

import javax.activation.MimetypesFileTypeMap;
import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;

import org.apache.commons.codec.binary.Base64;

import java.io.*;
import java.net.HttpURLConnection;
import java.net.URL;
import java.security.InvalidKeyException;
import java.security.NoSuchAlgorithmException;
import java.util.Iterator;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Map.Entry;

public class OSSPostFile {
	// The local file path to upload.
	private String localFilePath = "C:\\T\\1.txt";
	// OSS domain, such as http://oss-cn-hangzhou.aliyuncs.com
	private String endpoint = "http://oss-cn-beijing.aliyuncs.com";
	// Access key Id. Please get it from https://ak-console.aliyun.com
	private String accessKeyId = "";
	private String accessKeySecret = "";
	// The existing bucket name
	private String bucketName = "您自己的bucket名称";
	// The key name for the file to upload.
	private String key = "1.txt";

	public void PostObject() throws Exception {
		// append the 'bucketname.' prior to the domain, such as
		// http://bucket1.oss-cn-hangzhou.aliyuncs.com.
		String urlStr = endpoint.replace("http://", "http://" + bucketName + ".");

		// form fields
		Map<String, String> formFields = new LinkedHashMap<String, String>();

		// key
		formFields.put("key", this.key);
		// Content-Disposition
		formFields.put("Content-Disposition", "attachment;filename=" + localFilePath);
		// OSSAccessKeyId
		formFields.put("OSSAccessKeyId", accessKeyId);
		// policy
		String policy = "{\"expiration\": \"2120-01-01T12:00:00.000Z\",\"conditions\": [[\"content-length-range\", 0, 104857600000]]}";
		String encodePolicy = new String(Base64.encodeBase64(policy.getBytes()));
		formFields.put("policy", encodePolicy);
		// Signature
		String signaturecom = computeSignature(accessKeySecret, encodePolicy);
		formFields.put("Signature", signaturecom);

		String ret = formUpload(urlStr, formFields, localFilePath);

		System.out.println("Post Object [" + this.key + "] to bucket [" + bucketName + "]");
		System.out.println("post reponse:" + ret);
	}

	private static String computeSignature(String accessKeySecret, String encodePolicy)
			throws UnsupportedEncodingException, NoSuchAlgorithmException, InvalidKeyException {
		// convert to UTF-8
		byte[] key = accessKeySecret.getBytes("UTF-8");
		byte[] data = encodePolicy.getBytes("UTF-8");

		// hmac-sha1
		Mac mac = Mac.getInstance("HmacSHA1");
		mac.init(new SecretKeySpec(key, "HmacSHA1"));
		byte[] sha = mac.doFinal(data);

		// base64
		return new String(Base64.encodeBase64(sha));
	}

	private static String formUpload(String urlStr, Map<String, String> formFields, String localFile) throws Exception {
		String res = "";
		HttpURLConnection conn = null;
		String boundary = "9431149156168";

		try {
			URL url = new URL(urlStr);
			conn = (HttpURLConnection) url.openConnection();
			conn.setConnectTimeout(5000);
			conn.setReadTimeout(30000);
			conn.setDoOutput(true);
			conn.setDoInput(true);
			conn.setRequestMethod("POST");
			conn.setRequestProperty("User-Agent", "Mozilla/5.0 (Windows; U; Windows NT 6.1; zh-CN; rv:1.9.2.6)");
			conn.setRequestProperty("Content-Type", "multipart/form-data; boundary=" + boundary);
			OutputStream out = new DataOutputStream(conn.getOutputStream());

			// text
			if (formFields != null) {
				StringBuffer strBuf = new StringBuffer();
				Iterator<Entry<String, String>> iter = formFields.entrySet().iterator();
				int i = 0;

				while (iter.hasNext()) {
					Entry<String, String> entry = iter.next();
					String inputName = entry.getKey();
					String inputValue = entry.getValue();

					if (inputValue == null) {
						continue;
					}

					if (i == 0) {
						strBuf.append("--").append(boundary).append("\r\n");
						strBuf.append("Content-Disposition: form-data; name=\"" + inputName + "\"\r\n\r\n");
						strBuf.append(inputValue);
					} else {
						strBuf.append("\r\n").append("--").append(boundary).append("\r\n");
						strBuf.append("Content-Disposition: form-data; name=\"" + inputName + "\"\r\n\r\n");
						strBuf.append(inputValue);
					}

					i++;
				}
				out.write(strBuf.toString().getBytes());
			}

			StringBuffer strBuf1 = new StringBuffer();
			String callback = "{\"callbackUrl\":\"http://47.93.116.168/Revice.ashx\",\"callbackBody\":\"{\\\"bucket\\\"=${bucket},\\\"size\\\"=${size}}\"}";

			byte[] textByte = callback.getBytes("UTF-8");
			strBuf1.append("\r\n").append("--").append(boundary).append("\r\n");

			String callbackstr = new String(Base64.encodeBase64(textByte));
			strBuf1.append("Content-Disposition: form-data; name=\"callback\"\r\n\r\n" + callbackstr + "\r\n\r\n");
			out.write(strBuf1.toString().getBytes());

			// file
			File file = new File(localFile);
			String filename = file.getName();
			String contentType = new MimetypesFileTypeMap().getContentType(file);
			if (contentType == null || contentType.equals("")) {
				contentType = "application/octet-stream";
			}

			StringBuffer strBuf = new StringBuffer();
			strBuf.append("\r\n").append("--").append(boundary).append("\r\n");
			strBuf.append("Content-Disposition: form-data; name=\"file\"; " + "filename=\"" + filename + "\"\r\n");
			strBuf.append("Content-Type: " + contentType + "\r\n\r\n");
			out.write(strBuf.toString().getBytes());

			DataInputStream in = new DataInputStream(new FileInputStream(file));
			int bytes = 0;
			byte[] bufferOut = new byte[1024];
			while ((bytes = in.read(bufferOut)) != -1) {
				out.write(bufferOut, 0, bytes);
			}
			in.close();

			byte[] endData = ("\r\n--" + boundary + "--\r\n").getBytes();
			out.write(endData);
			out.flush();
			out.close();

			// Gets the file data
			strBuf = new StringBuffer();
			BufferedReader reader = new BufferedReader(new InputStreamReader(conn.getInputStream()));
			String line = null;
			while ((line = reader.readLine()) != null) {
				strBuf.append(line).append("\n");
			}
			res = strBuf.toString();
			reader.close();
			reader = null;
		} catch (Exception e) {
			System.err.println("Send post request exception: " + e.getLocalizedMessage());
			throw e;
		} finally {
			if (conn != null) {
				conn.disconnect();
				conn = null;
			}
		}

		return res;
	}

}
