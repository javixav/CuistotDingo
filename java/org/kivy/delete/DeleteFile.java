package org.kivy.delete;
import org.kivy.android.PythonActivity;
import android.app.Activity;
import android.widget.Toast; // be aware that toast does not work in all threads
import android.database.Cursor;
import android.app.PendingIntent;
import android.app.RecoverableSecurityException;
import android.content.pm.ApplicationInfo;

import android.content.ContentResolver;
import android.content.Context;
import android.content.IntentSender;
import android.net.Uri;
import android.os.Build;
import android.provider.MediaStore;

import java.io.File;
import java.io.FileNotFoundException;
import java.net.URI;

import android.util.Log;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.UUID;


// import androidx.activity.result.IntentSenderRequest;
// import androidx.activity.result.ActivityResultLauncher;

// import javax.print.attribute.standard.Media;


/**
 * source code :  https://www.youtube.com/watch?v=fsd3GEFqcbE&ab_channel=DeveloperExc
 * Some methods here needs androidx but androidx is tricky to activate, needs a graddle_options file like in camerax
 * that is why we use method1 thats seems to be working ? even if it is hard to replicate the not overwiting image bug
 * 
 */

public class DeleteFile {

	public static void deleteMethod1(Activity activity, Uri uri, int requestCode)
    throws SecurityException, IntentSender.SendIntentException, IllegalArgumentException{
		Context context = (Context) PythonActivity.mActivity;
		final ContentResolver resolver = context.getContentResolver();
		String stringUri = uri.toString();
		System.out.println(" -----------------0--------------- : uri string method 1 : " + stringUri);
		if (Build.VERSION.SDK_INT == Build.VERSION_CODES.Q)
		{
			try
			{
				// In Android == Q a RecoverableSecurityException is thrown for not-owned.
				// For a batch request the deletion will stop at the failed not-owned
				// file, so you may want to restrict deletion in Android Q to only
				// 1 file at a time, to make the experience less ugly.
				// Fortunately this gets solved in Android R.

				System.out.println(" -----------------1--------------- : trying to delete : ");
				resolver.delete(uri, null, null);
				}

			catch (RecoverableSecurityException ex)
			{
				String stackTrace = Log.getStackTraceString(ex); 
				System.out.println(" -----------------2--------------- : exception in method 1 : " + stackTrace);
				final IntentSender intent = ex.getUserAction()
				.getActionIntent()
				.getIntentSender();
				
				// IMPORTANT: still need to perform the actual deletion
				// as usual, so again getContentResolver().delete(...),
				// in your 'onActivityResult' callback, as in Android Q
				// all this extra code is necessary 'only' to get the permission,
				// as the system doesn't perform any actual deletion at all.
				// The onActivityResult doesn't have the target Uri, so you
				// need to cache it somewhere.
				activity.startIntentSenderForResult(intent, requestCode, null, 0, 0, 0, null);
				System.out.println(" -----------------3--------------- : requestCode method 1 is  : " +  Integer.toString(requestCode));
			}
		}
		else
		{
			// As usual for older APIs
			resolver.delete(uri, null, null);
		}
	}
	
	public void deleteMethod2(Activity activity, Uri uri){
		// error the import android.app.Activity seems to raise a error
		Context context = (Context) PythonActivity.mActivity;
		ContentResolver contentResolver = context.getContentResolver();
		String stringUri = uri.toString();
		
		try {
			contentResolver.delete(uri, null, null);

		} catch (SecurityException e) {
			String stackTrace = Log.getStackTraceString(e); 
			PendingIntent pendingIntent = null;
			if (Build.VERSION.SDK_INT>=Build.VERSION_CODES.R) {
				ArrayList<Uri> uris = new ArrayList<>();
				uris.add(uri);
				pendingIntent = MediaStore.createDeleteRequest(contentResolver, uris);
				// pendingIntent = MediaStore.createDeleteRequest(getContentResolver(), uris);

			}else{
				if( e instanceof RecoverableSecurityException){
					RecoverableSecurityException exception = (RecoverableSecurityException) e;
					pendingIntent = exception.getUserAction().getActionIntent();
				}
			}
			if (pendingIntent != null){
				IntentSender intentSender = pendingIntent.getIntentSender();
				try {

					activity.startIntentSenderForResult(intentSender, 100, null, 0, 0, 0);
					// startIntentSenderForResult(intentSender, 100, null, 0, 0, 0);
				} catch (IntentSender.SendIntentException ex) {
					ex.printStackTrace();
				}

			}
		}
	}


	// public void deleteMethod3(Uri uri) {
	// 	// IntentSenderRequest comes from androidx
	// 	Context context = (Context) PythonActivity.mActivity;
	// 	ContentResolver resolver = context.getContentResolver();
	// 	try {
	// 		resolver.delete(uri, null, null);
	// 	} catch (SecurityException securityException) {
	// 		if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
	// 			RecoverableSecurityException recoverableSecurityException = (RecoverableSecurityException) securityException;
	// 			IntentSenderRequest senderRequest = new IntentSenderRequest.Builder(recoverableSecurityException.getUserAction().getActionIntent().getIntentSender()).build();
	// 			deleteResultLauncher.launch(senderRequest); //Use of ActivityResultLauncher
	// 		}
	// 	}

	// 	final ActivityResultLauncher<IntentSenderRequest> deleteResultLauncher = registerForActivityResult(
	// 		new ActivityResultContracts.StartIntentSenderForResult(),
	// 		new ActivityResultCallback<ActivityResult>() {
	// 			@Override
	// 			public void onActivityResult(ActivityResult result) {
	// 				// RESULT_OK is an android constant = -1
	// 				if (result.getResultCode() == -1){
	// 				}
	// 			}
	// 		}
	// 	);
	// }

	
	// public static void deleteMethod4(Context context, Uri uri) {
	// 	// https://medium.com/@vishrut.goyani9/scoped-storage-in-android-writing-deleting-media-files-ee6235d30117
	// 	ContentResolver resolver = context.getContentResolver();
	// 	try {
	// 		resolver.delete(uri, null, null);
	// 	} catch (SecurityException securityException) {
	// 		if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
	// 			RecoverableSecurityException recoverableSecurityException = (RecoverableSecurityException) securityException;
	// 			IntentSenderRequest senderRequest = new IntentSenderRequest.Builder(recoverableSecurityException.getUserAction()
	// 		.getActionIntent().getIntentSender()).build();
	// 			deleteResultLauncher.launch(senderRequest); //Use of ActivityResultLauncher
	// 		}
	// 	}
	// }

}
