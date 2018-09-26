package hanli;

import java.io.UnsupportedEncodingException;
import java.net.URLEncoder;

import com.alibaba.fastjson.JSONObject;
import com.aliyuncs.DefaultAcsClient;
import com.aliyuncs.IAcsClient;
import com.aliyuncs.exceptions.ClientException;
import com.aliyuncs.exceptions.ServerException;
import com.aliyuncs.mts.model.v20140618.SubmitMediaInfoJobRequest;
import com.aliyuncs.mts.model.v20140618.SubmitMediaInfoJobResponse;
import com.aliyuncs.profile.DefaultProfile;

public class SubmitMediaInfoJob{

	private static String accessKeyId = "";
	private static String accessKeySecret = "";
	private static String mpsRegionId = "cn-hangzhou";
	private static String pipelineId = "0asdas9asdasd";
	private static String ossLocation = "oss-cn-hangzhou";
	private static String ossBucket = "bucket";
	private static String ossInputObject = "test/first/second/7061932.mp4";

	public static void main(String[] args) {
		// DefaultAcsClient
		DefaultProfile profile = DefaultProfile.getProfile(mpsRegionId, // Region
																		// ID
				accessKeyId, // AccessKey ID
				accessKeySecret); // Access Key Secret
		IAcsClient client = new DefaultAcsClient(profile);
		// request
		SubmitMediaInfoJobRequest request = new SubmitMediaInfoJobRequest();
		// Input
		JSONObject input = new JSONObject();
		input.put("Location", ossLocation);
		input.put("Bucket", ossBucket);
		try {
			input.put("Object", URLEncoder.encode(ossInputObject, "utf-8"));
		} catch (UnsupportedEncodingException e) {
			throw new RuntimeException("input URL encode failed");
		}
		request.setInput(input.toJSONString());

		// PipelineId
		// request.setPipelineId(pipelineId);
		// call api
		SubmitMediaInfoJobResponse response;
		try {
			response = client.getAcsResponse(request);
			System.out.println("RequestId is:" + response.getMediaInfoJob().getProperties().getBitrate());
			System.out.println("RequestId is:" + response.getMediaInfoJob().getProperties().getDuration());
			System.out
					.println("RequestId is:" + response.getMediaInfoJob().getProperties().getFormat().getFormatName());
			System.out.println("RequestId is:" + response.getMediaInfoJob().getInput().getObject());
		} catch (ServerException e) {
			e.printStackTrace();
		} catch (ClientException e) {
			e.printStackTrace();
		}
	}
}

