package org.kivy.camerax;

import org.kivy.android.PythonActivity;

import android.content.ContentResolver;
import android.content.Context;
import android.net.Uri;
import androidx.exifinterface.media.ExifInterface;

import java.io.IOException;
import java.io.InputStream;

/**
 * source code :  
 * 
 * https://developer.android.com/reference/androidx/exifinterface/media/ExifInterface
 * https://stackoverflow.com/questions/64421518/android-11-get-image-orientation-from-exif
 * 
 */

public class ImageExif {

	public int getOrientationExif(Uri uri) {
		Context context = (Context) PythonActivity.mActivity;
		ContentResolver contentResolver = context.getContentResolver();
		ExifInterface exif = null;
		int orientation  = 111;
		try {
			InputStream inputStream = contentResolver.openInputStream(uri);
			if (inputStream != null) {
				exif = new ExifInterface(inputStream);
			}
		} catch (IOException e) {
			e.printStackTrace();
		}

		if (exif != null) {
			orientation = exif.getAttributeInt(
				ExifInterface.TAG_ORIENTATION,
				ExifInterface.ORIENTATION_NORMAL
			);

			// switch (orientation) {
			// 	case ExifInterface.ORIENTATION_ROTATE_90:
			// 		return 90F;
			// 	case ExifInterface.ORIENTATION_ROTATE_180:
			// 		return 180F;
			// 	case ExifInterface.ORIENTATION_ROTATE_270:
			// 		return 270F;
			// 	default:
			// 		return 0F;
			// }
		}
		return orientation;
	}

}
