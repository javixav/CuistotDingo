package org.kivy.library;


import org.kivy.android.PythonActivity;
import android.app.Activity;
import android.widget.Toast;
import android.database.Cursor;
import android.app.PendingIntent;
import android.app.RecoverableSecurityException;
import android.content.pm.ApplicationInfo;

import android.content.ContentResolver;
import android.content.Context;
import android.content.ContentUris;
import android.content.IntentSender;
import android.net.Uri;
import android.os.Build;
import android.provider.MediaStore;
import android.provider.OpenableColumns;

import java.io.File;
import java.io.FileNotFoundException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.UUID;
import java.util.logging.Level;
import java.util.logging.Logger;


// import androidx.activity.result.IntentSenderRequest;
// import androidx.activity.result.ActivityResultLauncher;

// import javax.print.attribute.standard.Media;

import android.widget.Toast;

/**
 * This file are general method usefull to be used for any other project 
 */

public class BiblioJava4Android {
	// getContentResolver is a method from class  android.content.Content
	private static final Logger logger = Logger.getLogger(BiblioJava4Android.class.getName());

	public void showToast() {
		Context context = (Context) PythonActivity.mActivity;
		CharSequence text = "Toast : ";
		Toast toast = Toast.makeText(context, text, Toast.LENGTH_SHORT);
		toast.show();
	}
	
	public static Uri getUriFromFilePath(String filePath) {
		// android.os.FileUriExposedException because path starts with file://storage/emulated/0/Documents
		// and not content://storage/emulated/0/Documents ...
        File file = new File(filePath);
		Uri fileUri = Uri.fromFile(file); 
        return fileUri;
    }

	public Uri getUriFromDisplayName(Uri extUri, Context context, String displayName) {
		//source https://stackoverflow.com/questions/57098964/how-to-get-image-uri-in-android-q
		String[] projection;
		projection = new String[]{MediaStore.Files.FileColumns._ID};
	
		// TODO This will break if we have no matching item in the MediaStore.
		Cursor cursor = context.getContentResolver().query(extUri, projection,
				MediaStore.Files.FileColumns.DISPLAY_NAME + " LIKE ?", new String[]{displayName}, null);
		assert cursor != null;
		cursor.moveToFirst();
	
		if (cursor.getCount() > 0) {
			int columnIndex = cursor.getColumnIndex(projection[0]);
			long fileId = cursor.getLong(columnIndex);
	
			cursor.close();
			return Uri.parse(extUri.toString() + "/" + fileId);
		} else {
			return null;
		}
	
	};

	public List<Uri> getUrisFromSharedFolder(Context context, String folderName) {
		// folderName example : "Documents/appname/folder1/folderName"
		List<Uri> uris = new ArrayList<>();
		Uri collection;
		// Example for Pictures folder, adjust for other shared folders
		collection = MediaStore.Files.getContentUri(MediaStore.VOLUME_EXTERNAL);

		String[] projection = new String[] { MediaStore.Files.FileColumns._ID, MediaStore.Files.FileColumns.DISPLAY_NAME };
		String selection = MediaStore.Files.FileColumns.RELATIVE_PATH + " LIKE ?";
		String[] selectionArgs = new String[] { "%" + folderName + "%" }; // Adjust as needed for specific subfolders

		try (Cursor cursor = context.getContentResolver().query(
				collection,
				projection,
				selection,
				selectionArgs,
				null
		)) {
			if (cursor != null) {
				int idColumn = cursor.getColumnIndexOrThrow(MediaStore.Files.FileColumns._ID);
				while (cursor.moveToNext()) {
					long id = cursor.getLong(idColumn);
					Uri contentUri = Uri.withAppendedPath(collection, String.valueOf(id));
					uris.add(contentUri);
				}
			}
		}
		return uris;
}
	
	public String getFileNameFromUri(Uri uri, Context context) {
		String fileName = "Unknown";
		ContentResolver contentResolver = context.getContentResolver();
		try (Cursor cursor = contentResolver.query(uri, null, null, null, null)) {
			if (cursor != null && cursor.moveToFirst()) {
				int nameIndex = cursor.getColumnIndex(OpenableColumns.DISPLAY_NAME);
				if (nameIndex >= 0) {
					fileName = cursor.getString(nameIndex);
				}
			}
		} catch (Exception e) {
			e.printStackTrace();
		}
		return fileName;
	}

	public static Uri getUriFromAbsoluteFilePath(Context context, String filePath) {
		// filepath must be a Environment.getExternalStorageDirectory().getAbsolutePath() path
		long fileId;
		Uri contentUri = null;
		
		// // Check if the file exists first (optional, but good practice)
		// File file = new File(filePath);
		// if (!file.exists()) {
		// 	return null;
		// }

		// Determine the general content URI based on the file's media type if possible, 
		// or use a generic one like MediaStore.Files.getContentUri("external")
		// For images: 
		Uri externalUri = MediaStore.Images.Media.EXTERNAL_CONTENT_URI;
		// For general files (Android Q+ might require different handling):
		// Uri externalUri = MediaStore.Files.getContentUri("external"); 

		String[] projection = {MediaStore.Images.Media._ID};
		String selection = MediaStore.Images.Media.DATA + "=?";
		String[] selectionArgs = new String[]{filePath};
		String sortOrder = null; // No sort order needed

		try (Cursor cursor = context.getContentResolver().query(
			externalUri,
			projection,
			selection,
			selectionArgs,
			sortOrder
		)) {
			if (cursor != null && cursor.moveToFirst()) {
				int columnIndex = cursor.getColumnIndexOrThrow(MediaStore.Images.Media._ID);
				fileId = cursor.getLong(columnIndex);
				
				// Build the specific content URI for the found file ID
				contentUri = Uri.withAppendedPath(externalUri, String.valueOf(fileId));
			}
		} catch (Exception e) {
			e.printStackTrace();
			return null;
		}

		return contentUri;
	}

	public Uri getMediaStoreUriFromFilePath(Context context, String filePath) {
		// seems to work with relative and getAbsolutePath Tested and ok
		Uri contentUri = null;
		String[] projection = { MediaStore.Images.Media._ID };

		// Query the MediaStore for the file path
		Cursor cursor = context.getContentResolver().query(
			MediaStore.Images.Media.EXTERNAL_CONTENT_URI,
			projection,
			MediaStore.Images.Media.DATA + "=?",
			new String[] { filePath },
			null
		);

		if (cursor != null && cursor.moveToFirst()) {
			int columnIndex = cursor.getColumnIndexOrThrow(MediaStore.Images.Media._ID);
			long fileId = cursor.getLong(columnIndex);
			contentUri = ContentUris.withAppendedId(MediaStore.Images.Media.EXTERNAL_CONTENT_URI, fileId);
			cursor.close();
		}
		// If not found in Images, you might need to check Audio or Video MediaStore as well

		return contentUri;
	}

}
